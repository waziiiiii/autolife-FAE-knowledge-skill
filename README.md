# Autolife Knowledge Base Skill

Codex Skill for retrieving context from the Autolife knowledge base (AstrBot RAG).

## Quick Install

```bash
git clone https://github.com/waziiiiii/autolife-knowledge-skill.git
```

Copy the folder to your Codex skills directory and restart Codex.

Or install directly:

```bash
codex skill install-from-github waziiiiii/autolife-knowledge-skill
```

## What It Does

1. Queries the Autolife knowledge base hosted on AstrBot.
2. Returns relevant document chunks with source citations.
3. Codex uses the context to answer Autolife-related questions accurately.

## Coverage

- Autolife-S2 robot manuals
- Space capsule product specs
- Exhibition/staffing plans
- Flow robotic arm documentation
- Product feeding system docs

## Configuration

Works out of the box. Override with environment variables if needed:

```bash
export KB_BASE_URL=http://100.98.140.155:6185
export KB_USERNAME=autolife
export KB_PASSWORD=Autolife@1819
export KB_NAMES=autolife-docs
export KB_TOP_K=5
```

## Test

```bash
python scripts/retrieve_kb.py "太空舱产品"
```