"""Provider layer tests against a local mock of the OpenAI chat-completions API.

Run:  python3 -m tests.test_providers   (from the ib-marker directory)
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import grader, providers  # noqa: E402
from app.rubrics import get_rubric, resolve_rubric  # noqa: E402


class MockHandler(BaseHTTPRequestHandler):
    calls: list[dict] = []

    def log_message(self, *args):  # silence
        pass

    def _send(self, status: int, payload: dict) -> None:
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):  # noqa: N802
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        MockHandler.calls.append({"path": self.path, "auth": self.headers.get("Authorization"), "headers": dict(self.headers), "body": body})
        model = body.get("model", "")
        if self.headers.get("Authorization") != "Bearer good-key":
            return self._send(401, {"error": {"message": "Invalid API key"}})
        if not self.path.endswith("/chat/completions"):
            return self._send(404, {"error": {"message": "not found"}})
        if model == "missing-model":
            return self._send(404, {"error": {"message": f"The model `{model}` does not exist"}})
        if model == "tiny-tpm":
            return self._send(413, {"error": {"message": "Request too large for model on tokens per minute (TPM): Limit 8000, Requested 15000"}})
        if model == "busy":
            return self._send(429, {"error": {"message": "Rate limit reached for requests"}})
        if model == "strict" and ("response_format" in body or "max_tokens" in body):
            return self._send(400, {"error": {"message": "Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead."}})
        if model == "empty":
            return self._send(200, {"choices": [{"message": {"role": "assistant", "content": "", "reasoning_content": "..."}, "finish_reason": "length"}]})
        user = body["messages"][-1]["content"]
        if "Reply with the single word OK" in user:
            return self._send(200, {"choices": [{"message": {"role": "assistant", "content": "OK"}, "finish_reason": "stop"}]})
        codes = re.findall(r"^Criterion (\S+):", user, flags=re.M)
        crits = [{"code": c, "mark": 1, "band": "", "justification": "mock", "evidence": [], "strengths": ["s"], "improvements": ["i"]} for c in codes]
        result = {
            "document_summary": {"title": "T", "summary": "The student investigates rationing.", "matches_selected_rubric": True},
            "criteria": crits, "overall_strengths": ["x"],
            "priority_improvements": [{"priority": 1, "area": "a", "action": "b", "criteria": codes[:1]}],
            "integrity_flags": [], "confidence": "medium", "confidence_reason": "mock",
        }
        content = "<think>Let me plan the JSON { carefully }</think>\n```json\n" + json.dumps(result) + "\n```"
        return self._send(200, {"choices": [{"message": {"role": "assistant", "content": content}, "finish_reason": "stop"}]})


def main() -> None:
    failures = 0

    def check(cond: bool, msg: str) -> None:
        nonlocal failures
        print(("PASS " if cond else "FAIL ") + msg)
        if not cond:
            failures += 1

    # ---- preset registry -------------------------------------------------
    pub = providers.public_providers()
    check(len(pub) >= 10 and all(p["name"] and p["group"] for p in pub), f"{len(pub)} provider presets published")
    groups = {g for g, _ in providers.GROUPS}
    check(all(p["group"] in groups for p in pub), "every preset belongs to a known group")
    free_ids = [p["id"] for p in pub if p["group"] == "free"]
    check({"gemini", "mistral", "cohere", "nvidia", "openrouter"} <= set(free_ids), f"recommended free tiers present: {free_ids}")
    g = providers.resolve("gemini")
    check(g["base_url"].endswith("/openai") and g["model"] == "gemini-2.5-flash" and g["requires_key"], "gemini resolves to its OpenAI-compatible endpoint and default model")
    check(providers.resolve("groq")["max_doc_chars"] == 7000, "groq has a document cap")
    check(providers.resolve("ollama")["requires_key"] is False, "ollama needs no key")
    c = providers.resolve("custom", model="m", base_url="http://x/v1/")
    check(c["base_url"] == "http://x/v1", "custom base url trailing slash stripped")
    for bad in ({"provider_id": "nope"}, {"provider_id": "custom", "model": "m"}, {"provider_id": "lmstudio"}):
        try:
            providers.resolve(**bad)
            check(False, f"resolve rejects {bad}")
        except providers.ProviderError:
            check(True, f"resolve rejects {bad}")
    check(providers.resolve("gemini", base_url="http://evil/v1")["base_url"] == g["base_url"], "fixed presets ignore base url overrides")

    # ---- mock server ----------------------------------------------------
    server = HTTPServer(("127.0.0.1", 0), MockHandler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}/v1"

    def prov(model: str = "mock-model", pid: str = "custom") -> dict:
        p = providers.resolve(pid, model=model, base_url=base) if pid == "custom" else providers.resolve(pid, model=model)
        if pid != "custom":
            p["base_url"] = base
        return p

    ee = resolve_rubric(get_rubric("ee-2027"), None)
    doc = {"text": "Research question: To what extent... Bibliography ...", "warnings": [], "word_count": 10, "pages": None}

    MockHandler.calls.clear()
    res = grader.run_analysis(ee, None, "History", None, doc, [], "e.docx", "", prov(), "good-key")
    check(res["total"]["max"] == 30 and res["total"]["mark"] == 5, f"end-to-end through mock endpoint: {res['total']['mark']}/30 with think tags and fences stripped")
    first = MockHandler.calls[0]["body"]
    check(first.get("response_format") == {"type": "json_object"} and first.get("max_tokens") == grader.MAX_OUTPUT_TOKENS, "first attempt asks for JSON mode and sets max_tokens")
    check(MockHandler.calls[0]["auth"] == "Bearer good-key", "bearer auth header sent")
    check(res["model"]["provider"] == "custom" and res["model"]["model"] == "mock-model", "result records provider and model")

    MockHandler.calls.clear()
    res = grader.run_analysis(ee, None, None, None, doc, [], "e.docx", "", prov("strict"), "good-key")
    bodies = [c["body"] for c in MockHandler.calls]
    check(res["total"]["mark"] == 5 and len(bodies) == 3 and "max_completion_tokens" in bodies[-1] and "response_format" not in bodies[-1],
          f"400 fallback: {len(bodies)} attempts, last used max_completion_tokens without response_format")

    MockHandler.calls.clear()
    orp = prov("mock-model", "openrouter")
    grader.run_analysis(ee, None, None, None, doc, [], "e.docx", "", orp, "good-key")
    check(MockHandler.calls[0]["headers"].get("X-Title") == "IB Marker", "preset extra headers are sent")

    def expect_error(model: str, fragment: str, key: str = "good-key") -> None:
        try:
            grader.run_analysis(ee, None, None, None, doc, [], "e.docx", "", prov(model), key)
            check(False, f"{model}: expected an error")
        except grader.GraderError as exc:
            check(fragment.lower() in str(exc).lower(), f"{model}: friendly error mentions '{fragment}' -> {str(exc)[:90]}")

    expect_error("mock-model", "rejected the API key", key="bad-key")
    expect_error("missing-model", "does not know the model name 'missing-model'")
    expect_error("tiny-tpm", "too long")
    expect_error("busy", "rate limit")
    expect_error("empty", "empty answer")

    t = grader.test_provider(prov(), "good-key")
    check(t["ok"] and t["reply"] == "OK" and t["model"] == "mock-model", "test_provider round trip")
    t2 = grader.test_provider(prov("empty"), "good-key")
    check(t2["ok"] and t2["note"], "test_provider tolerates an empty reply and explains it")

    down = providers.resolve("custom", model="m", base_url="http://127.0.0.1:1/v1")
    try:
        grader.test_provider(down, "k")
        check(False, "unreachable endpoint reported")
    except grader.GraderError as exc:
        check("could not reach" in str(exc).lower(), "unreachable endpoint reported")

    # ---- parser hardening ----------------------------------------------
    check(grader.parse_json_response("<think>{not json} </think> {\"a\": 1}")["a"] == 1, "think blocks containing braces are removed before parsing")
    check(grader.parse_json_response("<thinking>x</thinking>```json\n{\"b\": 2}\n```")["b"] == 2, "thinking tags plus fences handled")

    server.shutdown()
    print(f"\n{'ALL PASSED' if not failures else str(failures) + ' FAILED'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
