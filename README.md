# Autolife Knowledge Base Skill

Codex Skill for querying and contributing to the Autolife knowledge base (AstrBot RAG).

## Install

```bash
git clone https://github.com/waziiiiii/autolife-knowledge-skill.git
```

Copy to your Codex skills directory and restart Codex.

## Two Capabilities

### 1. Retrieve (query the KB)

```bash
python scripts/retrieve_kb.py "太空舱产品有哪些"
```

### 2. Contribute (upload repair reports)

After a repair/troubleshooting session, the agent automatically:
1. Summarizes the process as a structured Markdown document
2. Uploads it to the knowledge base for future retrieval

```bash
python scripts/upload_to_kb.py "repair-report.md"
# or pipe:
echo "# Fix Report\nRoot cause: DDS config mismatch" | python scripts/upload_to_kb.py - --title "Fix: Battery 100%"
```

## Configuration

Works out of the box. Override with env vars:

```bash
export KB_BASE_URL=http://100.98.140.155:6185
export KB_USERNAME=autolife
export KB_PASSWORD=Autolife@1819
export KB_NAMES=autolife-docs
export KB_TOP_K=5
```