# IB Marker

A web app for IB Diploma teachers. Upload a student's Word or PDF document, choose the component (Internal Assessment, Extended Essay or TOK), the subject and the guide version, and an AI examiner marks the work against the published IB criteria. The report gives, for each criterion, a mark, strengths and areas for improvement; a plain-language summary of what the student is researching; the total mark (with an indicative grade where the IB publishes boundaries); and a prioritised summary of what to improve.

## Run it

### Windows (easiest)

1. Install Python 3.11 or newer from https://www.python.org/downloads/ if you do not already have it. On the **first** installer screen tick **Add python.exe to PATH**, then click *Install Now*. (If typing `python` in Command Prompt opens the Microsoft Store, Python is not installed yet.)
2. Double-click `run_windows.bat` in this folder. It finds Python, creates a private environment in `.venv`, installs the packages, starts the server and opens http://localhost:8000 in your browser. Keep the black window open while you use the app; close it to stop.
3. If Windows Firewall asks whether to allow Python to accept connections, click *Allow* if colleagues on your network should be able to use the app from their own computers; otherwise *Cancel* (it still works on your own computer).

**"pip is not recognized" or "python is not recognized"** means Python is either not installed or was installed without the PATH box ticked. Reinstall from python.org with the box ticked, close and reopen Command Prompt, then run the script again. A quick check: `py -m pip --version` should print a version number.

### Mac and Linux

Run `./run.sh` from this folder (first `chmod +x run.sh` if needed). It does the same as the Windows script.

### By hand

```bash
cd ib-marker
python -m venv .venv
# Windows: .venv\Scripts\activate        Mac/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000. Python 3.10 or newer is required.

### If localhost does not load

`http://localhost:8000` only works on a computer where the server is actually running. Work through these in order.

| What you see | Likely cause | What to do |
|---|---|---|
| The black window flashes and disappears | The script was opened from inside the zip, or an error appeared too fast to read | Right-click the zip, *Extract All*, run the script from the extracted folder. To see the error, open Command Prompt in the folder (type `cmd` in the File Explorer address bar) and type `run_windows.bat` |
| "Python was not found" | Python is not installed or not on PATH | Install from python.org with *Add python.exe to PATH* ticked, reopen Command Prompt, run again |
| "Could not import module 'app.main'" | Commands were run from the wrong folder | `cd` into the `ib-marker` folder (the one containing `app`) first |
| "error while attempting to bind on address" or "address already in use" | Another program holds port 8000 | The launcher switches to port 8010 automatically; otherwise close the other program |
| Browser says "This site can't be reached" | The server is not running | Look at the black window: the last line must say `Uvicorn running on http://0.0.0.0:8000`. If it does, try `http://127.0.0.1:8000` and make sure the address starts with `http://`, not `https://` |
| Page loads but says no API key is set | Everything works | Add a key under *Settings* to generate marks |

### API keys: free tiers that work

The examiner runs on a large language model that you choose under *Settings*. Several providers give free API keys with no card. Because IB Marker sends whole documents (often 10,000 tokens or more) and expects a long JSON reply, only providers with a large per-request allowance are useful. The Settings dropdown lists these presets, in this order of preference:

| Provider | Free allowance (November 2026) | Data use on the free tier | Key |
|---|---|---|---|
| **Google Gemini** (AI Studio) | About 15 requests/min, up to 1,500/day on Flash models, 1M-token context. Pro models are no longer free. | Prompts may be used to improve Google products (not for EU, UK, EEA accounts). | https://aistudio.google.com/apikey |
| **Mistral** (Experiment plan) | About 1 request/s, 500k tokens/min, 1B tokens/month. Phone verification. | Used for training unless you opt out in the console under Settings, Privacy. | https://console.mistral.ai/api-keys |
| **Cohere** (trial key) | 20 requests/min, 1,000 calls/month, 256k context. Evaluation use only. | Check Cohere's terms. | https://dashboard.cohere.com/api-keys |
| **NVIDIA NIM** | About 40 requests/min for prototyping, large open models. Developer account with phone verification. | Terms allow NVIDIA to use content to improve its products. | https://build.nvidia.com |
| **OpenRouter** (`:free` models) | 20 requests/min, 50/day (1,000/day after a one-time $10 top-up). Low priority, model list changes. | Depends on the upstream provider; some train on prompts. | https://openrouter.ai/keys |
| **Groq** (free plan) | 30 requests/min but only about 8,000 tokens/min including the reply, so IB Marker sends only the first 1,200 words. | Not retained or used for training by default. | https://console.groq.com/keys |
| **Ollama** or **LM Studio** (local) | Unlimited and private; needs a PC with 8 to 16 GB of RAM and a downloaded model. Small models mark less reliably. | Nothing leaves your computer. | No key |

Not listed on purpose: Cerebras caps free context at 8k tokens, GitHub Models caps input at 8k and output at 4k, and Hugging Face's free credits are a few cents a month. All three reject or truncate a normal essay. Anthropic and OpenAI have no free tier but remain available as paid options.

**How to set one up.** Click *Settings*, pick the provider, open the key link, create a key (two minutes, no card for the free tiers), paste it, click *Test connection*, then *Save*. The key stays in your browser (local storage if "Remember" is ticked, otherwise for the session) and is sent to this server only with each request. The server never writes it to disk.

**Student privacy.** Free tiers generally allow the provider to use what you send to improve their models. Remove student names from documents before uploading, opt out of training where the provider offers it (Mistral, OpenRouter), and use a local model or a paid plan with no-training terms when confidentiality matters. Check your school's data-protection policy.

**Local models.** Install Ollama from https://ollama.com, run `ollama pull llama3.1:8b`, and set the environment variable `OLLAMA_CONTEXT_LENGTH=32768` before starting Ollama (Windows: `setx OLLAMA_CONTEXT_LENGTH 32768`, then restart Ollama). Without that, Ollama silently cuts long documents to 4,000 tokens. In LM Studio, set the context length to at least 32k when loading the model and enable the local server.

**Keys on the server instead.** Set `IB_<PROVIDER>_API_KEY` (for example `IB_GEMINI_API_KEY`, `IB_MISTRAL_API_KEY`, `IB_ANTHROPIC_API_KEY`) before starting, and every teacher using that server shares the key. Optional per-provider overrides: `IB_<PROVIDER>_MODEL` and `IB_<PROVIDER>_BASE_URL`.

Without any key the app still runs the deterministic pre-check (word count, research question, bibliography, citations, reflection form, contents page) and can show a fixed sample report.

## Hosting it online (one shared key, nothing for teachers to set up)

The app already supports a shared key. Set the provider's variable on the server, for example `IB_GEMINI_API_KEY`, and every visitor's Settings panel preselects that provider and says "using this server's built-in key". Two features protect that key:

- **Access code** (`IB_ACCESS_CODE`): a password the app asks for once per browser before running the examiner. Without it, visitors get only the pre-check and the sample report.
- **Rate limit** (`IB_RATE_LIMIT`, default 40): analyses per user per hour on the shared key, so one person cannot exhaust the free tier's daily quota. Teachers who paste their own key in Settings are not limited.

Marking runs as a background job: the browser submits the document, gets a job id, and polls every few seconds. No hosting platform's request timeout can cut off a long analysis.

### Why not Netlify on its own

Netlify serves static pages and runs serverless functions written in JavaScript, TypeScript or Go. It cannot run this Python server. Its synchronous functions stop after 10 seconds (26 on the Pro plan), background functions cannot send a result back to the browser, and proxy rewrites to another server also stop after 26 seconds. A marking call takes 30 to 120 seconds, so even a rewrite of the API in JavaScript would time out. Netlify can host the page if you want it there (see the last option below), but the API must run on a host that keeps a Python process alive.

### Recommended: Render (free, no card)

1. Put the `ib-marker` folder in a GitHub repository (github.com, *New repository*, then upload the files or push with git). The repository contains no secrets, but make it private if you prefer.
2. Create an account at https://render.com with your GitHub login.
3. Click *New*, then *Blueprint*, and choose the repository. Render reads `render.yaml` and asks for the two values it does not have: paste your Gemini key as `IB_GEMINI_API_KEY` and invent a password for `IB_ACCESS_CODE`. (Using another provider? Add its variable instead, for example `IB_MISTRAL_API_KEY`.)
4. Click *Apply*. After two or three minutes the service is live at an address like `https://ib-marker.onrender.com`. Share that address and the access code with colleagues. Nobody needs to enter a key.
5. To change the key later, open the service in Render, go to *Environment*, edit the value and save; Render restarts the app.

If you would rather configure it by hand: *New*, *Web Service*, pick the repository, runtime Python 3, build command `pip install -r requirements.txt`, start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`, instance type Free, then add the environment variables.

Free Render services sleep after 15 minutes without visitors and take up to a minute to wake, so the first teacher of the day waits briefly. The free allowance is 750 hours a month, enough for one service that sleeps when idle.

### Other hosts

- **Google Cloud Run**: `gcloud run deploy ib-marker --source . --allow-unauthenticated --timeout 900 --set-env-vars IB_GEMINI_API_KEY=...,IB_ACCESS_CODE=...` from this folder. Generous free tier, no sleeping, but a card is required on the Google Cloud account.
- **Any Docker host, including a school server**: the `Dockerfile` builds a container that honours the host's `PORT` variable. Pass the same environment variables.
- **A teacher's own PC on the school network**: `run_windows.bat` with the variables set in Windows (`setx IB_GEMINI_API_KEY ...`), reachable by colleagues at that PC's address on port 8000 while it is on.

### Page on Netlify, API on Render

Only worth doing if you want the Netlify address or its custom-domain handling. Deploy the API on Render as above and add `IB_CORS_ORIGINS=https://your-site.netlify.app` to its environment. In `app/static/config.js` set `window.IB_MARKER_API = "https://ib-marker.onrender.com"` (your Render address). Connect the repository to Netlify; `netlify.toml` builds the page from the static folder. The page then calls the Render API directly from the browser.

### Environment variables

| Variable | Meaning |
|---|---|
| `IB_<PROVIDER>_API_KEY` | Shared key for one provider: `IB_GEMINI_API_KEY`, `IB_MISTRAL_API_KEY`, `IB_COHERE_API_KEY`, `IB_NVIDIA_API_KEY`, `IB_OPENROUTER_API_KEY`, `IB_GROQ_API_KEY`, `IB_ANTHROPIC_API_KEY`, `IB_OPENAI_API_KEY` |
| `IB_ACCESS_CODE` | Password required to run analyses (strongly recommended with a shared key) |
| `IB_RATE_LIMIT` | Shared-key analyses per user per hour, default 40, `0` disables |
| `IB_DEFAULT_PROVIDER` | Provider to preselect; otherwise the first one with a server key |
| `IB_<PROVIDER>_MODEL`, `IB_<PROVIDER>_BASE_URL` | Override a preset's default model or endpoint |
| `IB_CORS_ORIGINS` | Comma-separated page origins allowed to call the API from another host |
| `PORT` | Port to listen on (set automatically by Render and Cloud Run) |

## What is in the box

| Path | Purpose |
|---|---|
| `app/rubrics.py` | Rubric library: 37 tasks covering the EE (2018 and 2027 guides), TOK essay and exhibition, and the internal assessments of every DP subject group, with criteria, mark allocations and level descriptors. Each rubric records the guide version it applies to and whether its descriptors are paraphrased from the guide or summarised. |
| `app/extract.py` | Text extraction for .docx (paragraphs, headings and tables in order), PDF (per page, with scanned-page detection), .txt and .md, plus the pre-check rules. |
| `app/providers.py` | Provider presets: endpoint, default models, key link, free-tier limits and data-use notes for Gemini, Mistral, Cohere, NVIDIA, OpenRouter, Groq, Ollama, LM Studio, Anthropic, OpenAI and custom endpoints. |
| `app/grader.py` | Builds the examiner prompt from the rubric and the document, calls the chosen provider (Anthropic or any OpenAI-compatible endpoint, with automatic fallbacks for providers that reject JSON mode or `max_tokens`), translates provider errors into plain language, parses the JSON reply (stripping hidden reasoning), clamps marks to each criterion's range, computes totals and bands. |
| `app/main.py` | FastAPI endpoints: `GET /api/rubrics`, `POST /api/analyse` (multipart; `dry_run=1` for pre-check only), `GET /api/sample`, `GET /api/health`. |
| `app/static/` | Single-page interface: component and subject pickers, rubric preview with descriptors, drag-and-drop upload, custom rubric builder, report view, print to PDF, Markdown and JSON export, recent analyses stored in the browser. |
| `tests/` | `test_pipeline.py` (extraction, pre-check, prompt building, scoring with a mock model), `test_providers.py` (provider presets and the HTTP client against a local mock of the chat-completions API), `test_server.py` (access code, rate limit, CORS and background jobs through the real FastAPI app). No API key needed. |
| `Dockerfile`, `render.yaml`, `netlify.toml`, `app/static/config.js` | Deployment: container image, Render blueprint with the environment variables, optional Netlify build for the page only, and the page's API address setting. |

## How marking works

1. The document text is extracted and the pre-checks run.
2. The selected rubric (filtered for level, with the right descriptors for SL or HL where they differ) and the document are sent to the model with a system prompt that describes IB best-fit, criterion-referenced marking: mark only what is evidenced, choose the band whose descriptor best fits, award the upper or lower mark within the band, quote evidence, phrase improvements as actions, flag formal problems, and never name the student.
3. The reply is validated: every criterion must be present, marks are clamped to the criterion's range and made whole numbers, criteria that cannot be judged from a document (performances, videos, audio) are excluded from the total, and the band label and total are recomputed server-side.
4. The report is rendered and can be printed, or exported as Markdown or JSON.

## Limits to keep in mind

- The marks are a starting point for the teacher's professional judgement. They are not IB marks and the IB's moderation decides final results.
- Images, graphs and photographs inside documents are not analysed; the examiner judges them from captions and surrounding text. Oral components can only be assessed from a transcript, and pronunciation cannot be judged from text.
- Scanned PDFs need OCR before upload.
- A few rubrics are summarised because the guide is new or the exact wording could not be verified from public sources (marked in the interface). Use the custom rubric option to enter the criteria from your own copy of the guide where needed.
- The word count is approximate and includes headings, tables and references, which the IB usually excludes.
"# ib-marker" 
