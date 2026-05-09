
## Project Structure

```
RFPilot/
├── docs/                          # Input documents
│   └── test_docs/
│       └── Bid1/                  # One folder per bid
├── output/
│   ├── extracted/                 # Final JSON results
│   └── parsed/                    # Intermediate Markdown files
├── rfpilot/
│   ├── agents/                    # Agent definitions and prompts
│   │   ├── structuring_agent.py   # MAP: extracts fields from chunks
│   │   ├── merger_agent.py        # REDUCE: merges partials per document
│   │   ├── consolidation_agent.py # GATHER: merges across all files
│   │   └── prompts.py             # All agent instruction strings
│   ├── chunker/                   # Smart Markdown chunker
│   │   └── chunker.py             # Handles Q&A, tables, prose, headings
│   ├── config/
│   │   ├── constants.py           # PROJECT_ROOT and path constants
│   │   └── settings.py            # Pydantic settings (env vars, model config)
│   ├── llm/
│   │   └── deepseek_client.py     # DeepSeek AsyncOpenAI client init
│   ├── parser/
│   │   └── doc_parser.py          # Docling PDF/HTML → Markdown
│   ├── pipeline/
│   │   ├── map_reduce.py          # map_phase(), reduce_phase(), process_single_file()
│   │   └── scatter_gather.py      # process_all_files() — top-level orchestration
│   ├── runners/
│   │   └── pipeline_runner.py     # run_pipeline_for_folder() entry function
│   └── schemas/
│       └── rfp_schema.py          # Pydantic RFPExtraction model with merge()
├── main.py                        # Entry point
├── pyproject.toml                 # Project metadata and dependencies
├── uv.lock                        # Pinned dependency lockfile
└── .env.example                   # Environment variable template
```
