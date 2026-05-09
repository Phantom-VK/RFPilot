# RFPilot

An agentic AI pipeline that extracts structured procurement data from RFP (Request for Proposal) documents. RFPilot parses PDF and HTML bid documents, chunks them intelligently, and uses a multi-agent Map→Reduce→Consolidate architecture powered by DeepSeek LLM to output clean, structured JSON.

---

## How It Works

```
docs/test_docs/Bid1/
  ├── main_rfp.pdf          ─┐
  ├── addendum_1.pdf         ├─► Parser (Docling) ─► Markdown ─► Chunker ─► Agents ─► output/extracted/Bid1_result.json
  └── bid_info.html         ─┘
```

1. **Parser** — Docling converts PDF and HTML files to structured Markdown (OCR-enabled)
2. **Chunker** — Smart RFP chunker splits Markdown by headings, Q&A blocks, tables, and prose
3. **Map Phase** — Structuring Agent processes chunk batches in parallel via `asyncio.gather()`
4. **Reduce Phase** — Merger Agent collapses partial extractions into one per-document JSON
5. **Consolidate Phase** — Consolidation Agent merges all documents (base RFP + addendums) into final output

---

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager
- A DeepSeek API key — get one at [platform.deepseek.com](https://platform.deepseek.com)
- CUDA-compatible GPU recommended (for Docling OCR (if enabled) via `onnxruntime-gpu`)

---

## Installation

### 1. Install `uv`

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone the repository

```bash
git clone https://github.com/your-username/rfpilot.git
cd rfpilot
```

### 3. Install dependencies

```bash
uv sync
```

`uv` reads `pyproject.toml` and `uv.lock` to install the exact pinned dependency tree — no manual `pip install` needed.

### 4. Set up environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

---

## Usage

### Run the pipeline

Place your RFP documents (PDF or HTML) in a folder.:
Example:
```
docs/
└── test_docs/
    └── Bid1/
        ├── main_rfp.pdf
        ├── addendum_1.pdf
        └── bid_info.html
```

Run the pipeline:

```bash
uv run python main.py
```

The input folder is currently set to `docs/test_docs/Bid1` in `main.py`. To change it, edit this line:

```python
input_dir = "docs/test_docs/Bid1"
```

### Output

Results are written to `output/extracted/`:

```
output/
├── extracted/
│   └── Bid1_result.json       ← final structured extraction
└── parsed/
    └── Bid1/
        ├── main_rfp.md        ← Docling-parsed Markdown
        └── addendum_1.md
```

### Output JSON structure

```json
{
  "bid_number": "JA-207652",
  "title": "Student and Staff Computing Devices",
  "due_date": "07/09/2024 02:00 PM CST",
  "bid_submission_type": "RFP",
  "term_of_bid": "3 years with renewal options",
  "pre_bid_meeting": null,
  "installation": "White glove delivery, asset decaling, etching on laptops",
  "bid_bond_requirement": null,
  "delivery_date": "Within agreed timelines per purchase order",
  "payment_terms": "Net 30",
  "additional_documentation": "Form 1295, W-9, MWBE forms, Insurance certificate",
  "mfg_for_registration": "Dell",
  "contract_or_cooperative": "Desktop, Laptop and Tablet 2015 Master Contract (060B540000Z)",
  "model_no": "Dell Latitude 5550, Dell Thunderbolt 4 Dock WD22TB4",
  "part_no": "SI# CC7802, WD22TB4",
  "product": "Laptops, docking stations, Chromebooks",
  "contact_info": {
    "name": "Tamaira Hawkins",
    "email": "thawkins@treasurer.state.md.us",
    "phone": "410-260-7533",
    "address": "80 Calvert Street, Room 109, Annapolis, MD 21401",
    "role": "Agency POC",
    "department": null
  },
  "company_name": "State of Maryland Treasurer's Office",
  "bid_summary": "...",
  "product_specification": "..."
}
```

## Documentation

- [Project Structure](docs/project_structure.md) — folder layout and module responsibilities
- [Dependencies & Configuration](docs/dependency_config.md) — package details and environment settings
- [Pipeline Architecture](docs/pipeline_architecture.md) - mermaid flowdiagram showcasing the whole pipeline architecture

## Notes

- **GPU**: OCR is currently disabled in the parser — Docling uses `DoclingParseV2DocumentBackend` 
  for fast native text extraction on text-based PDFs. `onnxruntime-gpu` and `torch` are listed 
  as dependencies for future OCR support on scanned documents. GPU is required when OCR is enabled.
- **DeepSeek model**: Use `deepseek-v4-flash` for extraction tasks. `deepseek-v4-pro` (R1) adds unnecessary latency via chain-of-thought for structured data extraction.
- **Addendum priority**: When multiple documents are in a folder, the pipeline treats the alphabetically-first file as the base RFP and subsequent files as addendums. Addendum fields override base RFP fields (last addendum wins on conflicts like `due_date`).
- **`uv.lock`**: Commit this file to version control. It guarantees reproducible installs across all machines.

