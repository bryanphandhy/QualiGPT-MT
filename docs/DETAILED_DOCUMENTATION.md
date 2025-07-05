# QualiGPT Web Application – Detailed Documentation

> **Audience:** Researchers, data scientists, and developers who want to understand, deploy, or extend QualiGPT beyond the quick-start instructions in the root README.

---

## 1. Project Goals & Scope

QualiGPT brings state-of-the-art conversational AI (OpenAI GPT-4o with a 128 k context window) to qualitative data analysis.  It automates **thematic analysis** across interviews, focus-groups, and social-media datasets while remaining:

* **Accessible** – zero-install web UI, runs in any modern browser
* **Transparent** – prompts & algorithms are open-source and well-documented
* **Extensible** – modular architecture lets you swap models, storage back-ends, or UI layers
* **Secure** – your data never leaves the server you control, API keys are kept in memory only

---

## 2. High-Level Architecture

```
+--------------+     HTTPS      +----------------+      TLS      +-----------------+
|   Browser    | <------------> |    Flask API   | <-----------> |  OpenAI API     |
| (index.html) |                | (qualigpt-web) |               |  (chat.complet.)|
+--------------+                +----------------+               +-----------------+
        ^                              |
        |  CSV/XLSX/DOCX upload        |   Pandas / NLTK / Prompt-engineering
        |                              v
        |                   +----------------+
        +------------------ |  AI Processor  |
                            +----------------+
```

* **Frontend** – a single static `index.html` file served by Flask; vanilla JS handles API calls.
* **Backend** – Flask routes orchestrate file upload, validation, AI calls, and export.
* **AI Processor** – prompt templates + the `OpenAI` Python SDK perform analysis.
* **Stateless** – no database; everything lives in memory for the duration of the request.

---

## 3. Repository Layout

| Path | Purpose |
|------|---------|
| `qualigpt-webapp.py` | Flask application (all API endpoints) |
| `templates/index.html` | Single-page front-end UI |
| `Dockerfile` & `docker-compose.yml` | Containerised production deployment |
| `graph/` | Marketing / documentation images |
| `memory-bank/` | Context files used by the AI assistant (not runtime dependencies) |
| `sample-*.{csv,xlsx,docx}` | Example datasets for testing |
| `requirements.txt` | Locked Python package versions |

---

## 4. Detailed Request Lifecycle

1. **API Key Validation** – UI hits `/test_api` with the user-supplied key.  A 10-token test chat ensures the key is valid before any costly processing.
2. **Data Upload** – `/upload_file` accepts CSV, XLSX, or DOCX up to 16 MB.  Files are loaded into **Pandas** or **python-docx**, converted to plaintext, and streamed back to the browser for a quick preview.
3. **User Configuration** – The browser sends `/analyze` a JSON payload containing:
   * `api_key`
   * `data_content` (flattened text)
   * `data_type` (`Interview`, `Focus Group`, or `Social Media Posts`)
   * `num_themes` (1-20)
   * `custom_prompt` (optional)
   * `enable_role_playing` (bool)
4. **Segmentation** – `split_into_segments()` tokenises the dataset using NLTK.  Segments are capped at 120 k tokens leaving ~8 k for prompts & response, well below GPT-4o's 128 k limit.
5. **Prompt Construction** – A data-type specific template (see **§7 Prompt Engineering**) is filled and prefixed with a _system_ message.
6. **OpenAI Chat Completion** – One call per segment; results are gathered in `all_responses`.
7. **Aggregation** – For multi-segment datasets a second summarisation call merges themes via `analyze_merged_responses()`.
8. **Streaming Back** – The final plain-text table is sent to the browser.  Optional `/export_csv` converts it into a CSV attachment.

---

## 5. Flask API Surface

| Method | Route | JSON / Form Fields | Description |
|--------|-------|--------------------|-------------|
| POST | `/test_api` | `{ api_key }` | 10-token ping to verify key validity |
| POST | `/upload_file` | `file` (multipart) | Accepts CSV/XLSX/DOCX and returns text preview + headers |
| POST | `/analyze` | See §4 | Performs thematic analysis via OpenAI |
| POST | `/export_csv` | `{ response }` | Converts GPT table output → CSV download |

All routes return `{ success: bool, ... }`.  Errors are JSON encoded with descriptive messages.

---

## 6. Prompt Engineering Strategy

Prompt templates live in the in-memory dict `PROMPTS` and are **strictly formatted** to force GPT-4o to output a delimiter-guarded table:

* Table starts & ends with `**********` → easy server-side parsing.
* Pipe-separated columns – parsable as CSV.
* Explicit ban on markdown / commentary – keeps output clean.

Three templates exist (Interview, Focus Group, Social Media) but you can add more by editing `PROMPTS` and pointing the UI's `dataType` radio to the new key.

---

## 7. Token Management & Scaling

* GPT-4o supports **128 k** context.  This implementation keeps a ~8 k safety margin.
* Token count ≈ word count using `nltk.word_tokenize` (fast and library-free fallback implemented).
* Large datasets are processed chunk-wise and later re-aggregated to avoid context blow-ups.

---

## 8. Deployment Options

### 8.1 Local Development

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python qualigpt-webapp.py  # http://localhost:5000
```

Live-reload: set `FLASK_ENV=development`.

### 8.2 Docker (single container)

```bash
docker build -t qualigpt .
docker run -p 5005:5000 qualigpt
```

### 8.3 Docker Compose (production-ready)

Port 5005 behind Gunicorn with 4 workers:

```bash
docker-compose up --build -d
```

Environment variables can be placed in a `.env` file:

```
FLASK_ENV=production
# Example: OPENAI_API_KEY=sk-...
```

---

## 9. Extending the Codebase

1. **Add support for new data types** – Create a new prompt in `PROMPTS` and add a radio option + internationalised label in `index.html`.
2. **Switch LLM provider** – Replace `OpenAI` client calls with your preferred SDK; keep the prompt interface identical for painless migration.
3. **Persistent storage** – Plug in PostgreSQL or Supabase if you need to retain uploads or analysis history.
4. **Analytics / Logging** – Wrap Flask routes with middleware to capture timings and OpenAI usage.

---

## 10. Testing

No unit tests are shipped yet; suggested roadmap:

* **Backend** – pytest fixtures simulating uploads, monkey-patching OpenAI client.
* **Frontend** – Cypress or Playwright for end-to-end flows.
* **Prompt Regression** – golden-file snapshots of GPT output per dataset to detect drift after template changes.

---

## 11. Security & Privacy

* All processing is **in-memory** – no upload is persisted to disk.
* API keys are received over HTTPS (if you terminate TLS) and exist for the life of the request only.
* No third-party calls except OpenAI.
* To add extra hardening, set `Content-Security-Policy` headers in Flask and host behind an Nginx reverse proxy.

---

## 12. FAQ

**Q: How large can my dataset be?**  
A: Roughly 1 M words (~120 k tokens).  Beyond that, segment merging may hit the 128 k limit.

**Q: Does QualiGPT support multiple concurrent users?**  
A: Yes.  The app is stateless; scale horizontally with replicas behind a load-balancer.

**Q: Can I use GPT-3.5-turbo to save cost?**  
A: Yes – set the `model` parameter in `qualigpt-webapp.py` but remember its 16 k context window.

---

## 13. Changelog & Roadmap

See `progress.md` for ongoing development notes.  Planned features:

* Rich charts & dashboards (D3.js)
* Collaborative real-time sessions (WebSockets)
* CLI mode for batch processing

---

## 14. License & Citation

MIT-licensed.  If you publish research using QualiGPT please cite:

> Zhang, H. _et al._ **QualiGPT**: An Open-Source AI Toolkit for Rapid Qualitative Thematic Analysis, 2024.

---

## 15. Provider Abstraction Layer

QualiGPT  now ships with a **pluggable LLM layer** defined in `llm_providers.py`.

| Provider | Class | Package | Notes |
|----------|-------|---------|-------|
| OpenAI GPT-4o | `OpenAIProvider` | `openai` | Default, 128 k context |
| Anthropic Claude 3 | `AnthropicProvider` | `anthropic` | Haiku by default; change model string for Sonnet / Opus |
| Google Gemini-Pro | `GeminiProvider` | `google-generativeai` | 32 k context; `max_tokens` defaults to 2048 |
| DeepSeek (placeholder) | `DeepSeekProvider` | – | Ready for future SDK |

The web UI exposes these via a dropdown. Backend routes accept a `provider` field (defaults to "openai"). Custom integrations are one subclass away – just implement `test_connection()` and `chat()`.

---

*Happy analysing!* 🚀 