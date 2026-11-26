"""IB Marker: FastAPI application."""

from __future__ import annotations

import collections
import hmac
import json
import os
import pathlib
import secrets
import threading
import time
from typing import Any

from fastapi import FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from . import grader, providers
from .extract import ExtractionError, count_words, extract_text, precheck
from .rubrics import EE_SUBJECT_GUIDANCE, get_rubric, resolve_rubric, rubric_summaries

BASE_DIR = pathlib.Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MAX_UPLOAD_BYTES = 20 * 1024 * 1024

# Deployment settings, all optional (see README, "Hosting it online").
ACCESS_CODE = os.environ.get("IB_ACCESS_CODE", "").strip()
CORS_ORIGINS = [o.strip() for o in os.environ.get("IB_CORS_ORIGINS", "").split(",") if o.strip()]
try:
    RATE_LIMIT = int(os.environ.get("IB_RATE_LIMIT", "40"))  # shared-key analyses per user per hour; 0 disables
except ValueError:
    RATE_LIMIT = 40
JOB_TTL_SECONDS = 3600

app = FastAPI(title="IB Marker", version="1.2.0", docs_url=None, redoc_url=None)
if CORS_ORIGINS:
    app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

_hits: dict[str, collections.deque] = collections.defaultdict(collections.deque)
_jobs: dict[str, dict[str, Any]] = {}
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _server_keys() -> dict[str, bool]:
    return {pid: bool(providers.server_key(pid)) for pid in providers.PROVIDERS}


def _check_access(code: str | None) -> None:
    if ACCESS_CODE and not hmac.compare_digest((code or "").strip().encode(), ACCESS_CODE.encode()):
        raise HTTPException(401, "This IB Marker server requires an access code. Enter the code from your coordinator in Settings and try again.")


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate(request: Request) -> None:
    """Limit analyses that use the server's shared key (users with their own key are not limited)."""
    if RATE_LIMIT <= 0:
        return
    ip = _client_ip(request)
    now = time.time()
    with _lock:
        q = _hits[ip]
        while q and now - q[0] > 3600:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            raise HTTPException(429, f"This server allows {RATE_LIMIT} analyses per hour for each user, to protect its shared API quota. Try again later, or add your own key in Settings.")
        q.append(now)


def _purge_jobs(now: float) -> None:
    with _lock:
        for jid in [j for j, job in _jobs.items() if now - job["created"] > JOB_TTL_SECONDS]:
            del _jobs[jid]


def _run_job(job_id: str, args: tuple) -> None:
    with _lock:
        _jobs[job_id]["status"] = "running"
    try:
        analysis = grader.run_analysis(*args)
        with _lock:
            _jobs[job_id].update(status="done", analysis=analysis)
    except grader.GraderError as exc:
        with _lock:
            _jobs[job_id].update(status="error", error=str(exc))
    except Exception as exc:  # pragma: no cover
        with _lock:
            _jobs[job_id].update(status="error", error=f"Unexpected error while marking: {type(exc).__name__}: {exc}")
    finally:
        with _lock:
            _jobs[job_id]["finished"] = time.time()


def _resolve_provider(provider: str, model: str, base_url: str, x_api_key: str | None) -> tuple[dict[str, Any], str]:
    try:
        prov = providers.resolve(provider, model, base_url)
    except providers.ProviderError as exc:
        raise HTTPException(400, str(exc)) from exc
    key = (x_api_key or "").strip() or providers.server_key(prov["id"]) or ""
    if prov["requires_key"] and not key:
        raise HTTPException(401, f"No API key is set for {prov['name']}. Open Settings, paste a key (free keys: {prov['key_url']}) and try again.")
    return prov, key


def _parse_custom_rubric(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise HTTPException(400, f"Custom rubric is not valid JSON: {exc}") from exc
    crits = data.get("criteria") or []
    if not isinstance(crits, list) or not crits:
        raise HTTPException(400, "Custom rubric needs at least one criterion.")
    norm = []
    for i, c in enumerate(crits):
        try:
            mx = int(c.get("max"))
        except (TypeError, ValueError, AttributeError) as exc:
            raise HTTPException(400, f"Criterion {i + 1} needs a numeric maximum mark.") from exc
        if mx < 1 or mx > 100:
            raise HTTPException(400, f"Criterion {i + 1}: maximum mark must be between 1 and 100.")
        code = str(c.get("code") or chr(65 + i)).strip()[:6]
        bands = c.get("bands") or []
        if not bands:
            desc = str(c.get("descriptor") or "").strip()
            bands = [{"marks": f"1-{mx}" if mx > 1 else "1", "text": desc or "Meets the criterion to the extent evidenced."}]
        norm.append({"code": code, "name": str(c.get("name") or f"Criterion {code}")[:120], "max": mx,
                     "focus": str(c.get("focus") or c.get("descriptor") or "")[:1000], "bands": bands, "assessable": True})
    rubric = {
        "id": "custom", "component": str(data.get("component") or "Custom rubric")[:80], "group": "Custom",
        "subject": str(data.get("subject") or "Custom")[:120], "task": str(data.get("task") or "Teacher-defined task")[:160],
        "version": "Teacher-defined", "levels": ["SL/HL"], "max_marks": sum(c["max"] for c in norm),
        "word_limit": int(data["word_limit"]) if str(data.get("word_limit") or "").isdigit() else None,
        "limit_note": str(data.get("limit_note") or "")[:500], "evidence_note": "", "notes": str(data.get("notes") or "")[:500],
        "fidelity": "teacher", "variants": None, "grade_bands": None, "weighting": "", "criteria": norm,
    }
    return rubric


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "version": app.version, "server_keys": _server_keys(), "default_provider": providers.default_provider(),
            "access_required": bool(ACCESS_CODE), "rate_limit": RATE_LIMIT}


@app.get("/api/providers")
def list_providers() -> dict[str, Any]:
    return {"providers": providers.public_providers(), "groups": providers.GROUPS,
            "server_keys": _server_keys(), "default_provider": providers.default_provider()}


@app.get("/api/rubrics")
def rubrics() -> dict[str, Any]:
    return {"rubrics": rubric_summaries(), "ee_subject_guidance": EE_SUBJECT_GUIDANCE}


@app.post("/api/analyse")
async def analyse(
    request: Request,
    file: UploadFile = File(...),
    rubric_id: str = Form(...),
    level: str = Form(""),
    variant: str = Form(""),
    teacher_notes: str = Form(""),
    custom_rubric: str = Form(""),
    dry_run: str = Form("0"),
    mode: str = Form("sync"),
    provider: str = Form(providers.DEFAULT_PROVIDER),
    model: str = Form(""),
    base_url: str = Form(""),
    x_api_key: str | None = Header(default=None),
    x_access_code: str | None = Header(default=None),
) -> JSONResponse:
    started = time.time()
    data = await file.read()
    if not data:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "The file is larger than 20 MB.")

    if rubric_id == "custom":
        if not custom_rubric:
            raise HTTPException(400, "Custom rubric data is missing.")
        base = _parse_custom_rubric(custom_rubric)
        rubric = resolve_rubric(base, None)
        variant_guidance = None
    else:
        base = get_rubric(rubric_id)
        if not base:
            raise HTTPException(404, f"Unknown rubric '{rubric_id}'.")
        lvl = level.strip() or None
        if lvl and lvl not in base["levels"] and "SL/HL" not in base["levels"]:
            raise HTTPException(400, f"Level '{lvl}' is not available for this rubric.")
        rubric = resolve_rubric(base, lvl)
        variant_guidance = EE_SUBJECT_GUIDANCE.get(variant) if base["component"] == "Extended Essay" else None

    try:
        doc = extract_text(file.filename or "upload", data)
    except ExtractionError as exc:
        raise HTTPException(422, str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(422, f"The document could not be read: {type(exc).__name__}") from exc

    checks = precheck(doc["text"], rubric, doc["word_count"])
    meta = {
        "filename": file.filename,
        "kind": doc["kind"],
        "pages": doc["pages"],
        "word_count": doc["word_count"],
        "truncated": doc["truncated"],
        "warnings": list(doc["warnings"]),
        "preview": doc["text"][:1200],
        "rubric": {k: rubric[k] for k in ("id", "component", "subject", "task", "version", "word_limit", "limit_note", "fidelity", "notes", "weighting", "assessable_max", "total_max")},
        "level": level or None,
        "variant": variant or None,
    }
    if dry_run == "1":
        return JSONResponse({"meta": meta, "precheck": checks, "analysis": None, "elapsed": round(time.time() - started, 1)})

    _check_access(x_access_code)
    prov, key = _resolve_provider(provider, model, base_url, x_api_key)
    if not (x_api_key or "").strip():
        _check_rate(request)

    model_doc = doc
    limit = prov.get("max_doc_chars")
    if limit and len(doc["text"]) > limit:
        model_doc = dict(doc)
        model_doc["text"] = doc["text"][:limit]
        sent_words = count_words(model_doc["text"])
        note = (f"Only the first {sent_words:,} words were sent to {prov['name']} because of its small per-request limit; "
                f"the marks reflect that portion only. Use Google Gemini or Mistral (both free) for full-length documents.")
        model_doc["warnings"] = list(doc["warnings"]) + [note]
        meta["warnings"].append(note)
        meta["sent_words"] = sent_words

    args = (rubric, level or None, variant or None, variant_guidance, model_doc, checks, file.filename or "upload", teacher_notes, prov, key)

    if mode == "async":
        now = time.time()
        _purge_jobs(now)
        job_id = secrets.token_urlsafe(16)
        with _lock:
            _jobs[job_id] = {"status": "queued", "created": now, "meta": meta, "precheck": checks, "provider": prov["name"]}
        threading.Thread(target=_run_job, args=(job_id, args), daemon=True).start()
        return JSONResponse({"job_id": job_id, "status": "queued", "meta": meta, "precheck": checks})

    try:
        analysis = await run_in_threadpool(grader.run_analysis, *args)
    except grader.GraderError as exc:
        raise HTTPException(502, str(exc)) from exc
    return JSONResponse({"meta": meta, "precheck": checks, "analysis": analysis, "elapsed": round(time.time() - started, 1)})


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str) -> dict[str, Any]:
    with _lock:
        job = _jobs.get(job_id)
        snapshot = dict(job) if job else None
    if not snapshot:
        raise HTTPException(404, "Unknown or expired job. Run the analysis again.")
    elapsed = round((snapshot.get("finished") or time.time()) - snapshot["created"], 1)
    out: dict[str, Any] = {"status": snapshot["status"], "elapsed": elapsed,
                           "stage": "Waiting to start…" if snapshot["status"] == "queued" else f"Marking with {snapshot['provider']}. This usually takes 30 to 120 seconds; free tiers can be slower."}
    if snapshot["status"] == "done":
        out.update(meta=snapshot["meta"], precheck=snapshot["precheck"], analysis=snapshot["analysis"])
    elif snapshot["status"] == "error":
        out["error"] = snapshot["error"]
    return out


@app.post("/api/test-provider")
async def test_provider(
    provider: str = Form(providers.DEFAULT_PROVIDER),
    model: str = Form(""),
    base_url: str = Form(""),
    x_api_key: str | None = Header(default=None),
    x_access_code: str | None = Header(default=None),
) -> dict[str, Any]:
    _check_access(x_access_code)
    try:
        prov, key = _resolve_provider(provider, model, base_url, x_api_key)
    except HTTPException as exc:
        return {"ok": False, "error": str(exc.detail)}
    try:
        return await run_in_threadpool(grader.test_provider, prov, key)
    except grader.GraderError as exc:
        return {"ok": False, "error": str(exc)}


@app.get("/api/sample")
def sample() -> dict[str, Any]:
    """A fixed sample report so the interface can be previewed without an API key."""
    path = BASE_DIR / "sample_report.json"
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)
