## Key Dependencies

| Package | Purpose |
|---|---|
| `docling` | PDF and HTML parsing with OCR support |
| `openai-agents` | OpenAI Agents SDK for multi-agent orchestration |
| `openai` | OpenAI-compatible API client (used with DeepSeek) |
| `onnxruntime-gpu` | GPU-accelerated OCR inference for Docling |
| `pydantic-settings` | Settings management from `.env` |
| `pymupdf` | Fallback PDF text extraction |
| `torch` | Required by Docling's ML models |

---

## Configuration

All tunable parameters live in `rfpilot/config/settings.py` and are overridable via `.env`:

| Setting | Default                    | Description |
|---|----------------------------|---|
| `DEEPSEEK_API_KEY` | —                          | Your DeepSeek API key (required) |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | API base URL |
| `DEEPSEEK_MODEL` | `deepseek-v4-flash`        | Model name |
| `MAX_CONCURRENCY` | `7`                        | Max parallel LLM calls (raise to 10–15 for speed) |
| `MAX_CHUNK_SIZE` | `1200`                     | Max characters per prose chunk |
| `QA_GROUP_SIZE` | `5`                        | Q&A pairs grouped per extraction call |

---