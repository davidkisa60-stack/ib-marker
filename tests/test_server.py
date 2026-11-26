"""HTTP-level tests of the deployment features: access code, shared-key rate limit, CORS and
background jobs. Uses FastAPI's TestClient, no network and no real key.

Run:  python3 -m tests.test_server   (from the ib-marker directory)
"""

from __future__ import annotations

import os
import pathlib
import sys
import time

os.environ["IB_ACCESS_CODE"] = "secret123"
os.environ["IB_RATE_LIMIT"] = "2"
os.environ["IB_MISTRAL_API_KEY"] = "server-side-key"
os.environ["IB_CORS_ORIGINS"] = "https://example.netlify.app"

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from tests.test_pipeline import make_docx  # noqa: E402

DOCX_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def main() -> None:
    failures = 0

    def check(cond: bool, msg: str) -> None:
        nonlocal failures
        print(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            failures += 1

    client = TestClient(app)
    docx = make_docx()

    def post(**kw):
        headers = kw.pop("headers", {})
        data = {"rubric_id": "ee-2027", "variant": "History", "provider": "custom", "model": "m", "base_url": "http://127.0.0.1:1/v1"}
        data.update(kw)
        return client.post("/api/analyse", data=data, files={"file": ("essay.docx", docx, DOCX_TYPE)}, headers=headers)

    h = client.get("/api/health").json()
    check(h["access_required"] is True and h["server_keys"]["mistral"] is True and h["default_provider"] == "mistral" and h["rate_limit"] == 2,
          "health reports access code, server key, default provider and rate limit")
    check(client.get("/api/providers").json()["default_provider"] == "mistral", "providers endpoint preselects the provider with a server key")

    r = post(dry_run="1")
    check(r.status_code == 200 and r.json()["analysis"] is None, "pre-check needs no access code")
    r = post()
    check(r.status_code == 401 and "access code" in r.json()["detail"].lower(), "real analysis without a code is refused")
    r = post(headers={"X-Access-Code": "wrong"})
    check(r.status_code == 401, "wrong code refused")
    r = post(headers={"X-Access-Code": "secret123"})
    check(r.status_code == 502 and "could not reach" in r.json()["detail"].lower(), "correct code reaches the provider (sync mode)")

    r = post(headers={"X-Access-Code": "secret123"}, mode="async")
    j = r.json()
    check(r.status_code == 200 and j.get("job_id") and j["status"] == "queued" and j["meta"]["word_count"] > 0, "async mode returns a job id with the pre-check")
    status = {}
    for _ in range(100):
        status = client.get(f"/api/jobs/{j['job_id']}").json()
        if status["status"] in ("done", "error"):
            break
        time.sleep(0.1)
    check(status["status"] == "error" and "could not reach" in status.get("error", "").lower(), f"job finishes with the provider's error ({status['status']})")

    r = post(headers={"X-Access-Code": "secret123"})
    check(r.status_code == 429 and "per hour" in r.json()["detail"], "third shared-key analysis within the hour is rate limited")
    r = post(headers={"X-Access-Code": "secret123", "X-API-Key": "own-key"})
    check(r.status_code == 502, "a user's own key is not rate limited")

    check(client.get("/api/jobs/does-not-exist").status_code == 404, "unknown job returns 404")

    r = client.post("/api/test-provider", data={"provider": "mistral"})
    check(r.status_code == 401, "connection test is also behind the access code")
    r = client.post("/api/test-provider", data={"provider": "custom", "model": "m", "base_url": "http://127.0.0.1:1/v1"}, headers={"X-Access-Code": "secret123"})
    check(r.status_code == 200 and r.json()["ok"] is False and "could not reach" in r.json()["error"].lower(), "connection test runs with the code")

    r = client.options("/api/analyse", headers={"Origin": "https://example.netlify.app", "Access-Control-Request-Method": "POST",
                                               "Access-Control-Request-Headers": "x-api-key,x-access-code"})
    check(r.status_code == 200 and r.headers.get("access-control-allow-origin") == "https://example.netlify.app", "CORS preflight allows the configured page origin")
    r = client.options("/api/analyse", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    check(r.headers.get("access-control-allow-origin") is None, "CORS does not allow other origins")

    page = client.get("/").text
    check('id="access-field"' in page and "/static/config.js" in page, "page includes the access-code field and config.js")
    check(client.get("/static/config.js").status_code == 200, "config.js is served")

    print(f"\n{'ALL PASSED' if not failures else str(failures) + ' FAILED'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
