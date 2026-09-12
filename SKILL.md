---
name: autolife-knowledge
description: >
  Retrieve supporting context from and contribute repair/troubleshooting records to the Autolife knowledge base.
  Use when the user asks about Autolife robots, Robox, 太空舱, products, manuals, FAE, exhibitions,
  robot troubleshooting, or after completing a repair/troubleshooting session.
---

# Autolife Knowledge Base

## NetBird Constraint

All remote KB access requires the self-hosted NetBird network:

```text
https://netbird.autolife-robotics.com:443
```

`retrieve_kb.py` and `upload_to_kb.py` run the NetBird preflight automatically. If it fails, ask the user to start or log in to NetBird; do not bypass it.

## Retrieve Context

Before answering Autolife-related questions, retrieve relevant context:

```bash
python scripts/retrieve_kb.py "your question"
```

Default: `http://100.98.140.155:6185`, KB `autolife-docs`, top 5 results.

Override with env vars: `KB_BASE_URL`, `KB_USERNAME`, `KB_PASSWORD`, `KB_NAMES`, `KB_TOP_K`.

## Contribute Knowledge (Post-Repair)

After completing a repair, troubleshooting session, or significant investigation, you MUST:
1. Summarize the process as a structured Markdown document
2. Upload it to the knowledge base:

```bash
python scripts/upload_to_kb.py "path/to/summary.md"
# or pipe from stdin:
cat summary.md | python scripts/upload_to_kb.py - --title "Fix: Battery Shows 100%"
```

### Summary Document Template

Follow this structure (based on real repair records):

```markdown
# [System/Component] [问题简述] 排查修复记录（编号）

**结论**：一句话说清根因和修复方式。

## 一、问题现象
- 机器人/设备标识
- 系统版本
- 故障日期
- 耗时
- 具体症状

## 二、排查过程
- 排查思路
- 每一步的实测结果
- 关键拐点/决定性测试

## 三、根因分析
- 直接原因
- 深层原因
- 因果链

## 四、修复步骤
- 改动前后对比
- 操作命令
- 回滚方案

## 五、验证结果
- 逐层验证项（打勾列表）

## 六、遗留事项与预防
- 遗留问题
- 下次遇到同类问题的快速判定法
```

### When to Write and Upload

- ✅ Robot hardware/software repair completed
- ✅ Complex debugging session with non-obvious root cause
- ✅ Configuration fix that other robots might need
- ✅ New finding about system architecture
- ❌ Simple restarts with no investigation
- ❌ Known issues already covered in KB

### Answering Rules

- Answer primarily from knowledge base content when relevant.
- Cite source document name for each fact.
- If context is insufficient, state what is missing.
- Do not guess when the KB does not cover the topic.
- Do not expose passwords or JWT tokens in output.
