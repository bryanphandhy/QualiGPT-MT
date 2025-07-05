# QualiGPT Web Application – Detailed Documentation

> **Audience:** Researchers, data scientists, and developers who want to understand, deploy, or extend QualiGPT beyond the quick-start instructions in the root README.

---

## 1. Project Goals & Scope

QualiGPT brings state-of-the-art conversational AI (OpenAI GPT-4o, Anthropic Claude, Google Gemini, DeepSeek) to qualitative data analysis.  It automates **thematic analysis** across interviews, focus-groups, and social-media datasets while remaining:

* **Accessible** – zero-install web UI, runs in any modern browser
* **Transparent** – prompts & algorithms are open-source and well-documented
* **Extensible** – modular architecture lets you swap models, storage back-ends, or UI layers
* **Secure** – your data never leaves the server you control, API keys are kept in memory only

---

## 2. High-Level Architecture

```
+--------------+     HTTPS      +----------------+      TLS      +-----------------+
|   Browser    | <------------> |    Flask API   | <-----------> |  LLM Providers  |
| (index.html) |                | (qualigpt-web) |               | (OpenAI, Claude,|
+--------------+                +----------------+               |  Gemini, DeepSeek)
        ^                              |
        |  CSV/XLSX/DOCX upload        |   Pandas / NLTK / Prompt-engineering
        |                              v
        |                   +----------------+
        +------------------ |  AI Processor  |
                            +----------------+
```

* **Frontend** – a single static `index.html` file served by Flask; vanilla JS handles API calls, table rendering, and export.
* **Backend** – Flask routes orchestrate file upload, validation, AI calls, and export.
* **AI Processor** – prompt templates + the selected LLM provider perform analysis.
* **Stateless** – no database; everything lives in memory for the duration of the request.

---

## 3. Repository Layout

| Path | Purpose |
|------|---------|
| `qualigpt-webapp.py` | Flask application (all API endpoints) |
| `templates/index.html` | Single-page front-end UI (interactive table, model selection, export) |
| `Dockerfile` & `docker-compose.yml` | Containerised production deployment |
| `graph/` | Marketing / documentation images |
| `memory-bank/` | Context files used by the AI assistant (not runtime dependencies) |
| `sample-*.{csv,xlsx,docx}` | Example datasets for testing |
| `requirements.txt` | Locked Python package versions |

---

## 4. Detailed Request Lifecycle

1. **API Key Validation** – UI hits `/test_api` with the user-supplied key and selected provider/model.  A test chat ensures the key is valid before any costly processing.
2. **Data Upload** – `/upload_file` accepts CSV, XLSX, or DOCX up to 16 MB.  Files are loaded into **Pandas** or **python-docx**, converted to plaintext, and streamed back to the browser for a quick preview.
3. **User Configuration** – The browser sends `/analyze` a JSON payload containing:
   * `api_key`
   * `provider` (OpenAI, Anthropic, Gemini, DeepSeek)
   * `model` (e.g., gpt-4o, gemini-2.5-flash, claude-3.5-sonnet)
   * `data_content` (flattened text)
   * `data_type` (`Interview`, `Focus Group`, or `Social Media Posts`)
   * `num_themes` (1-20)
   * `custom_prompt` (optional)
   * `enable_role_playing` (bool)
   * `temperature` (float)
   * `max_tokens` (int)
4. **Segmentation** – `split_into_segments()` tokenises the dataset using NLTK.  Segments are capped at 120 k tokens leaving ~8 k for prompts & response, well below LLM context limits.
5. **Prompt Construction** – A data-type specific template (see **§7 Prompt Engineering**) is filled and prefixed with a _system_ message.
6. **LLM Chat Completion** – One call per segment; results are gathered in `all_responses`.
7. **Aggregation** – For multi-segment datasets a second summarisation call merges themes via `analyze_merged_responses()`.
8. **Streaming Back** – The final plain-text table is sent to the browser.  The browser parses and renders it as an interactive table. CSV export is generated client-side for reliability.

---

## 5. Flask API Surface

| Method | Route | JSON / Form Fields | Description |
|--------|-------|--------------------|-------------|
| POST | `/test_api` | `{ api_key, provider, model }` | Test ping to verify key validity for the selected provider/model |
| POST | `/upload_file` | `file` (multipart) | Accepts CSV/XLSX/DOCX and returns text preview + headers |
| POST | `/analyze` | See §4 | Performs thematic analysis via selected LLM provider |

All routes return `{ success: bool, ... }`.  Errors are JSON encoded with descriptive messages.

---

## 6. Prompt Engineering Strategy

Prompt templates live in the in-memory dict `PROMPTS` and are **strictly formatted** to force the LLM to output a delimiter-guarded table:

* Table starts & ends with `**********` → easy client-side parsing.
* Pipe-separated columns – parsable as CSV.
* Explicit ban on markdown / commentary – keeps output clean.

Three templates exist (Interview, Focus Group, Social Media) but you can add more by editing `PROMPTS` and pointing the UI's `dataType` radio to the new key.

---

## 7. Token Management & Scaling

* LLMs support large context windows (e.g., GPT-4o: 128k, Gemini: 1M tokens).  This implementation keeps a safety margin.
* Token count ≈ word count using `nltk.word_tokenize` (fast and library-free fallback implemented).
* Large datasets are processed chunk-wise and later re-aggregated to avoid context blow-ups.

---

## 8. User Interface Features

- **Provider & Model Selection**: Choose from OpenAI, Anthropic, Gemini, DeepSeek and their latest models directly in the UI
- **Advanced Settings**: Adjust temperature and max tokens for each analysis
- **Interactive Results Table**: Sort, search, and filter your analysis results in a beautiful table
- **Reliable CSV Export**: Exports exactly what you see in the table, compatible with Excel/Sheets
- **Text Export**: Save the raw response and a formatted summary
- **View Toggle**: Switch between table and raw text view
- **Print Table**: Print a professional version of your results

---

## 9. Extending the Codebase

1. **Add support for new data types** – Create a new prompt in `PROMPTS` and add a radio option + internationalised label in `index.html`.
2. **Switch LLM provider** – Add a new provider class in `llm_providers.py` and update the UI dropdown.
3. **Persistent storage** – Plug in PostgreSQL or Supabase if you need to retain uploads or analysis history.
4. **Analytics / Logging** – Wrap Flask routes with middleware to capture timings and LLM usage.

---

## 10. Testing

No unit tests are shipped yet; suggested roadmap:

* **Backend** – pytest fixtures simulating uploads, monkey-patching LLM client.
* **Frontend** – Cypress or Playwright for end-to-end flows.
* **Prompt Regression** – golden-file snapshots of LLM output per dataset to detect drift after template changes.

---

## 11. Security & Privacy

* All processing is **in-memory** – no upload is persisted to disk.
* API keys are received over HTTPS (if you terminate TLS) and exist for the life of the request only.
* No third-party calls except the selected LLM provider.
* To add extra hardening, set `Content-Security-Policy` headers in Flask and host behind an Nginx reverse proxy.

---

## 12. FAQ

**Q: How large can my dataset be?**  
A: Roughly 1 M words (~120 k tokens).  Beyond that, segment merging may hit the LLM context limit.

**Q: Does QualiGPT support multiple concurrent users?**  
A: Yes.  The app is stateless; scale horizontally with replicas behind a load-balancer.

**Q: Can I use a cheaper model to save cost?**  
A: Yes – set the `model` parameter in the UI and backend; context window will depend on the model.

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

*Happy analysing!* 🚀 