---
name: autolife-knowledge
description: Retrieve supporting context from the Autolife knowledge base. Use when the user asks about Autolife robots, Robox, 太空舱, products, manuals, FAE, exhibitions, or explicitly asks to query the knowledge base.
---

# Autolife Knowledge Base

Before answering Autolife-related questions, retrieve relevant context from the knowledge base and use it as the primary source.

## Query Workflow

Run the retrieval script with the user's question:

```bash
python scripts/retrieve_kb.py "your question"
```

Default settings (no environment variables needed):

- Base URL: `http://100.98.140.155:6185`
- Username: `autolife`
- Password: `Autolife@1819`
- KB name: `autolife-docs`
- Top K: `5`

Environment variable overrides:

- `KB_BASE_URL`
- `KB_USERNAME`
- `KB_PASSWORD`
- `KB_NAMES` (comma-separated, defaults to `autolife-docs`)
- `KB_TOP_K`

## Answering Rules

- If the retrieved context is relevant, answer primarily from the knowledge base.
- Cite source document name for each fact, e.g. `Autolife-S2 使用手册.txt`.
- If the retrieved context is insufficient, list what was found and what is missing.
- Do not infer or guess when the knowledge base does not cover the topic.
- Do not expose passwords or JWT tokens in the final answer.