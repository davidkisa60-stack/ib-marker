"""Model provider presets for IB Marker.

Each preset describes how to reach a provider's chat endpoint (OpenAI-compatible or
Anthropic), sensible default models, where to get a key, and the practical limits and
data-use terms of its free tier as understood in November 2026. Limits change often:
the Settings panel shows these notes, but the provider's own dashboard is authoritative.

Environment overrides (optional, per provider id in upper case):
  IB_<ID>_API_KEY   server-side key used when the browser sends none
  IB_<ID>_MODEL     default model
  IB_<ID>_BASE_URL  endpoint override
"""

from __future__ import annotations

import os
from typing import Any

GROUPS: list[tuple[str, str]] = [
    ("free", "Free tiers (recommended)"),
    ("free_limited", "Free, short documents only"),
    ("local", "Runs on your computer (free, private)"),
    ("paid", "Paid"),
    ("custom", "Other"),
]

DEFAULT_PROVIDER = "gemini"


class ProviderError(Exception):
    pass


def _p(**kw: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "api": "openai",
        "base_url": "",
        "base_url_editable": False,
        "default_model": "",
        "models": [],
        "key_url": "",
        "requires_key": True,
        "limits": "",
        "privacy": "",
        "notes": "",
        "max_doc_chars": None,
        "extra_headers": {},
        "extra_body": {},
    }
    base.update(kw)
    return base


PROVIDERS: dict[str, dict[str, Any]] = {
    "gemini": _p(
        name="Google Gemini (AI Studio free tier)",
        group="free",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        default_model="gemini-2.5-flash",
        models=["gemini-2.5-flash", "gemini-3-flash-preview", "gemini-3.1-flash-lite", "gemini-2.5-flash-lite"],
        key_url="https://aistudio.google.com/apikey",
        limits="Free tier: about 15 requests per minute and up to 1,500 per day on Flash models, with a 1 million-token context, so whole essays fit easily. No card needed. Pro models are no longer free.",
        privacy="On the free tier Google may use what you send to improve its products (not for accounts in the EU, UK or EEA). Remove student names before uploading.",
        notes="Best all-round free option for full-length work.",
    ),
    "mistral": _p(
        name="Mistral (Experiment plan, free)",
        group="free",
        base_url="https://api.mistral.ai/v1",
        default_model="mistral-large-latest",
        models=["mistral-large-latest", "mistral-medium-latest", "mistral-small-latest", "magistral-medium-latest"],
        key_url="https://console.mistral.ai/api-keys",
        limits="Free Experiment plan: about 1 request per second, 500,000 tokens per minute and 1 billion tokens per month, with long context. Needs phone verification, no card.",
        privacy="Your data is used to train Mistral models unless you opt out under Settings, Privacy in the Mistral console. Do that before uploading student work.",
        notes="Generous limits and large models; good for whole portfolios.",
    ),
    "cohere": _p(
        name="Cohere (trial key, free)",
        group="free",
        base_url="https://api.cohere.ai/compatibility/v1",
        default_model="command-a-03-2025",
        models=["command-a-03-2025", "command-r-plus-08-2024", "command-r7b-12-2024"],
        key_url="https://dashboard.cohere.com/api-keys",
        limits="Trial key: 20 requests per minute and 1,000 calls per month, 256,000-token context. No card needed; for evaluation use only.",
        privacy="Trial keys are for evaluation; check Cohere's data-use terms before uploading student work.",
    ),
    "nvidia": _p(
        name="NVIDIA NIM (build.nvidia.com, free)",
        group="free",
        base_url="https://integrate.api.nvidia.com/v1",
        default_model="openai/gpt-oss-120b",
        models=["openai/gpt-oss-120b", "meta/llama-3.3-70b-instruct", "qwen/qwen3-235b-a22b", "deepseek-ai/deepseek-v3.1", "nvidia/llama-3.3-nemotron-super-49b-v1.5"],
        key_url="https://build.nvidia.com",
        limits="Free for prototyping with an NVIDIA Developer account (phone verification): roughly 40 requests per minute, large open models with long context. Your personal limit is shown at the top of build.nvidia.com.",
        privacy="NVIDIA's trial terms allow it to use submitted content to improve its products. Remove student names before uploading.",
    ),
    "openrouter": _p(
        name="OpenRouter (free models)",
        group="free",
        base_url="https://openrouter.ai/api/v1",
        default_model="openai/gpt-oss-120b:free",
        models=["openai/gpt-oss-120b:free", "openrouter/free", "meta-llama/llama-3.3-70b-instruct:free", "qwen/qwen3-next-80b-a3b-instruct:free", "nvidia/nemotron-3-ultra:free"],
        key_url="https://openrouter.ai/keys",
        limits="Models whose name ends in :free cost nothing: 20 requests per minute and 50 per day (1,000 per day after a one-time $10 top-up). Free endpoints are served at low priority, so expect occasional 'busy' errors, and the list of free models changes.",
        privacy="Depends on which company serves the free model; some may train on prompts. You can restrict this in OpenRouter's privacy settings.",
        extra_headers={"HTTP-Referer": "https://github.com/ib-marker", "X-Title": "IB Marker"},
    ),
    "groq": _p(
        name="Groq (free plan)",
        group="free_limited",
        base_url="https://api.groq.com/openai/v1",
        default_model="openai/gpt-oss-120b",
        models=["openai/gpt-oss-120b", "openai/gpt-oss-20b", "moonshotai/kimi-k2-instruct-0905", "qwen/qwen3-32b"],
        key_url="https://console.groq.com/keys",
        limits="Free plan: 30 requests per minute and 1,000 per day, but only about 8,000 tokens per minute including the reply. A full essay plus the rubric does not fit, so IB Marker sends only the first 1,200 words or so to Groq. Use Gemini or Mistral for full-length work.",
        privacy="Groq does not retain or train on API data by default.",
        max_doc_chars=7000,
    ),
    "ollama": _p(
        name="Ollama on this computer (free, private)",
        group="local",
        base_url="http://localhost:11434/v1",
        base_url_editable=True,
        default_model="llama3.1:8b",
        models=["llama3.1:8b", "qwen3:8b", "gemma3:12b", "mistral-small3.2", "gpt-oss:20b"],
        key_url="https://ollama.com/download",
        requires_key=False,
        limits="Nothing leaves your computer. Install Ollama, run 'ollama pull llama3.1:8b' (8B models need about 8 GB of RAM), and set the environment variable OLLAMA_CONTEXT_LENGTH=32768 before starting Ollama, otherwise long documents are silently cut off.",
        privacy="Fully private: the document never leaves the machine running IB Marker.",
        notes="Small local models mark less reliably than cloud models; treat their output as a first pass.",
    ),
    "lmstudio": _p(
        name="LM Studio on this computer (free, private)",
        group="local",
        base_url="http://localhost:1234/v1",
        base_url_editable=True,
        default_model="",
        models=[],
        key_url="https://lmstudio.ai",
        requires_key=False,
        limits="Start LM Studio, load a model with a context length of at least 32k, and switch on the local server in the Developer tab. Enter the model identifier shown in that tab.",
        privacy="Fully private: the document never leaves the machine running IB Marker.",
    ),
    "anthropic": _p(
        name="Anthropic Claude (paid)",
        group="paid",
        api="anthropic",
        base_url="https://api.anthropic.com",
        default_model="claude-fable-5-1",
        models=["claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-4-5-20251001"],
        key_url="https://console.anthropic.com/settings/keys",
        limits="Pay as you go; no free tier. Highest-quality marking.",
        privacy="API data is not used for training by default.",
    ),
    "openai": _p(
        name="OpenAI (paid)",
        group="paid",
        base_url="https://api.openai.com/v1",
        default_model="gpt-5",
        models=["gpt-5", "gpt-5-mini", "gpt-4.1"],
        key_url="https://platform.openai.com/api-keys",
        limits="Pay as you go; no free tier.",
        privacy="API data is not used for training by default.",
    ),
    "custom": _p(
        name="Other OpenAI-compatible endpoint",
        group="custom",
        base_url="",
        base_url_editable=True,
        default_model="",
        requires_key=False,
        limits="Any server that speaks the OpenAI chat-completions API: enter its base URL (usually ending in /v1), the model name, and a key if it needs one.",
    ),
}


def _env(pid: str, suffix: str) -> str | None:
    return os.environ.get(f"IB_{pid.upper()}_{suffix}") or None


def server_key(pid: str) -> str | None:
    return _env(pid, "API_KEY") if pid in PROVIDERS else None


PREFERRED_ORDER = ["gemini", "mistral", "cohere", "nvidia", "openrouter", "groq", "anthropic", "openai", "ollama", "lmstudio", "custom"]


def default_provider() -> str:
    """Provider to preselect in the interface.

    IB_DEFAULT_PROVIDER wins if set; otherwise the first preferred provider that has a
    server-side key (so a shared deployment needs no setup by teachers); otherwise Gemini.
    """
    forced = (os.environ.get("IB_DEFAULT_PROVIDER") or "").strip().lower()
    if forced in PROVIDERS:
        return forced
    for pid in PREFERRED_ORDER:
        if server_key(pid):
            return pid
    return DEFAULT_PROVIDER


def public_providers() -> list[dict[str, Any]]:
    out = []
    for pid, p in PROVIDERS.items():
        out.append({
            "id": pid,
            "name": p["name"],
            "group": p["group"],
            "api": p["api"],
            "base_url": _env(pid, "BASE_URL") or p["base_url"],
            "base_url_editable": p["base_url_editable"],
            "default_model": _env(pid, "MODEL") or p["default_model"],
            "models": p["models"],
            "key_url": p["key_url"],
            "requires_key": p["requires_key"],
            "limits": p["limits"],
            "privacy": p["privacy"],
            "notes": p["notes"],
            "max_doc_chars": p["max_doc_chars"],
        })
    return out


def resolve(provider_id: str | None, model: str | None = None, base_url: str | None = None) -> dict[str, Any]:
    """Turn a provider id plus optional overrides into a concrete call target."""
    pid = (provider_id or "").strip().lower() or DEFAULT_PROVIDER
    p = PROVIDERS.get(pid)
    if not p:
        raise ProviderError(f"Unknown provider '{provider_id}'. Choose one in Settings.")
    url = _env(pid, "BASE_URL") or p["base_url"]
    if p["base_url_editable"] and (base_url or "").strip():
        url = base_url.strip()
    url = url.rstrip("/")
    if p["api"] == "openai" and not url:
        raise ProviderError("Enter the provider's base URL in Settings (for example http://localhost:1234/v1).")
    chosen_model = (model or "").strip() or _env(pid, "MODEL") or p["default_model"]
    if not chosen_model:
        raise ProviderError(f"Enter a model name for {p['name']} in Settings.")
    return {
        "id": pid,
        "name": p["name"],
        "group": p["group"],
        "api": p["api"],
        "base_url": url,
        "model": chosen_model,
        "extra_headers": dict(p["extra_headers"]),
        "extra_body": dict(p["extra_body"]),
        "requires_key": p["requires_key"],
        "max_doc_chars": p["max_doc_chars"],
        "key_url": p["key_url"],
    }
