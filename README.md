# Autolife FAE Knowledge Skill

这是一个 Codex Skill，用于从 Autolife FAE 知识库检索机器人、太空舱、产品手册、部署配置和故障处理经验，并在完成维修或复杂排查后，把新的经验文档写入 AstrBot RAG 知识库。

## 功能概览

- **知识库检索**：把自然语言问题发送到远端 AstrBot Dashboard API，返回最相关的知识片段和来源文档名。
- **经验文档上传**：把维修/排查 Markdown 上传到 AstrBot 知识库，等待后台分块和向量化完成。
- **NetBird 强制预检**：所有访问远端知识库的操作前，先确认本机已连接到指定自托管 NetBird 服务器。
- **修复后沉淀**：提供统一的问题排查、根因、修复、验证和遗留事项文档结构，便于后续检索。

## 总体架构

```text
Codex / 用户
    |
    |  本地 Python Skill
    v
NetBird 客户端
    |
    |  自托管 NetBird 虚拟局域网
    |  Management: https://netbird.autolife-robotics.com:443
    v
远端 AstrBot Dashboard
    |  http://100.98.140.155:6185
    |
    +-- POST /api/auth/login                         登录，获取 JWT
    +-- POST /api/kb/retrieve                        检索知识片段
    +-- GET  /api/kb/list                            根据知识库名称查找 KB ID
    +-- POST /api/kb/document/upload                 创建上传任务
    `-- GET  /api/kb/document/upload/progress        查询分块/向量化进度
```

脚本本身只使用 Python 标准库，不依赖第三方包。

## 项目结构

```text
.
├── SKILL.md                          # Codex Skill 行为约束和使用入口
├── README.md                         # 本文档
├── agents/openai.yaml                # Agent 元数据
└── scripts/
    ├── netbird_preflight.py          # NetBird 连接预检
    ├── retrieve_kb.py                # 检索远端知识库
    └── upload_to_kb.py               # 上传 Markdown 并等待向量化完成
```

## NetBird 约束

远端 AstrBot 只能通过 NetBird 虚拟局域网访问。脚本在检索和上传前都会调用 `ensure_netbird()`，确认以下条件全部成立：

1. 本机能找到 `netbird` CLI。
2. NetBird daemon 已连接。
3. Management 通道已连接。
4. Signal 通道已连接。
5. Management URL 是自托管地址。
6. NetBird 会话未过期。

默认只允许：

```text
https://netbird.autolife-robotics.com:443
```

任何一项失败都会阻止访问知识库。此时应先启动 NetBird、切换到正确 Profile 或重新登录，不要改用公网地址。

手动预检：

```powershell
python scripts/netbird_preflight.py
```

## 安装

把本仓库克隆或复制到 Codex Skill 目录，然后重启 Codex：

```text
C:\Users\<用户名>\.codex\skills\autolife-FAE-knowledge-skill
```

推荐环境：

- Windows 10/11
- Python 3.10 或更新版本
- 已登录自托管 NetBird
- 可访问远端 AstrBot Dashboard

## 配置

所有脚本通过环境变量读取配置。不要把真实密码提交到仓库。

| 环境变量 | 默认值 | 说明 |
|---|---|---|
| `KB_BASE_URL` | `http://100.98.140.155:6185` | AstrBot Dashboard API 地址。 |
| `KB_USERNAME` | `autolife` | AstrBot 登录用户名；已内置默认值。 |
| `KB_PASSWORD` | `123455` | AstrBot 登录密码；已内置默认值。 |
| `KB_NAMES` | `autolife-docs` | 默认知识库名称。 |
| `KB_TOP_K` | `5` | 检索返回的最大片段数。 |
| `NETBIRD_MANAGEMENT_URL` | `https://netbird.autolife-robotics.com:443` | 允许使用的 NetBird 管理服务器。 |

当前 PowerShell 会话覆盖示例：

```powershell
$env:KB_USERNAME = "other-account"
$env:KB_PASSWORD = "other-password"
$env:KB_NAMES = "autolife-docs"
```

用户级永久覆盖示例：

```powershell
[Environment]::SetEnvironmentVariable("KB_USERNAME", "other-account", "User")
[Environment]::SetEnvironmentVariable("KB_PASSWORD", "other-password", "User")
[Environment]::SetEnvironmentVariable("KB_NAMES", "autolife-docs", "User")
```

永久变量设置后，需要重启终端和 Codex。

## 检索流程

```powershell
python scripts/retrieve_kb.py "太空舱饮品配置在哪里配置"
```

指定返回数量和服务地址：

```powershell
python scripts/retrieve_kb.py "机器人视觉无法启动" --top-k 8
```

内部流程：

1. 执行 NetBird 预检。
2. 调用 `POST /api/auth/login` 获取 JWT。
3. 调用 `POST /api/kb/retrieve`，传入问题、知识库名称列表和 `top_k`。
4. 解析 `data.context_text`；如果服务返回 `data.results`，则格式化为带序号、来源文档名和分数的片段。
5. 输出检索结果，供 Codex 组织回答。

Codex 回答规则：

- 相关内容优先以知识库为准。
- 引用事实时说明来源文档名。
- 知识库没有覆盖的内容必须明确说明，不能编造。
- 不输出密码、JWT 或原始登录响应。

## 上传流程

### 上传本地 Markdown

```powershell
python scripts/upload_to_kb.py "C:\path\to\repair-report.md"
```

指定知识库和标题：

```powershell
python scripts/upload_to_kb.py "C:\path\to\repair-report.md" `
  --kb-name autolife-docs `
  --title "Fix: 机器人启动后视觉服务退出.md"
```

从标准输入上传：

```powershell
Get-Content "summary.md" -Raw | python scripts/upload_to_kb.py - --title "Fix: DDS 配置不匹配.md"
```

### 内部步骤

1. 执行 NetBird 预检。
2. 使用内置账号或环境变量覆盖值。
3. 读取本地文件，或从标准输入创建临时 Markdown 文件。
4. 登录 AstrBot Dashboard。
5. 调用 `GET /api/kb/list`，把 `--kb-name` 解析成 KB ID。
6. 调用 `POST /api/kb/document/upload`，以 `multipart/form-data` 上传文件。
7. 从响应中读取 `data.task_id`。
8. 轮询 `GET /api/kb/document/upload/progress`，直到任务 `completed` 或 `failed`。
9. 如果后台结果里有失败文档，脚本返回错误；否则输出处理结果。

后台任务默认最多等待 15 分钟，用于覆盖较大的文档、分块和 embedding 耗时。

## 修复后沉淀流程

完成维修、复杂排查、配置修复或重要架构验证后，应先生成结构化 Markdown，再上传到知识库。

推荐文档结构：

```markdown
# [系统/组件] [问题简述] 排查修复记录

**结论**：一句话说明根因和修复方式。

## 一、问题现象
- 机器人/设备标识
- 系统版本
- 故障日期
- 耗时
- 具体症状

## 二、排查过程
- 排查思路
- 每一步实测结果
- 关键拐点和决定性测试

## 三、根因分析
- 直接原因
- 深层原因
- 因果链

## 四、修复步骤
- 改动前后对比
- 操作命令
- 回滚方案

## 五、验证结果
- 逐层验证项
- 验证命令和输出摘要

## 六、遗留事项与预防
- 遗留问题
- 后续观察点
- 下次快速判定方法
```

适合上传的情况：

- 硬件或软件维修完成。
- 复杂调试找到了非显而易见的根因。
- 配置修复对其他机器人有复用价值。
- 发现了新的系统架构限制或部署要求。

不建议上传的情况：

- 简单重启且没有新的排查结论。
- 知识库已有同因、同修法的记录。
- 内容只有临时猜测，没有验证结果。

## 接口说明

| 接口 | 方法 | 用途 |
|---|---|---|
| `/api/auth/login` | `POST` | 用户名密码登录，返回 JWT。 |
| `/api/kb/retrieve` | `POST` | 按问题和知识库名称检索片段。 |
| `/api/kb/list` | `GET` | 列出知识库，用于名称转 ID。 |
| `/api/kb/document/upload` | `POST` | 上传文档并创建后台处理任务。 |
| `/api/kb/document/upload/progress` | `GET` | 查询后台任务进度和结果。 |

## 本地验证

语法检查：

```powershell
python -m py_compile scripts/netbird_preflight.py scripts/retrieve_kb.py scripts/upload_to_kb.py
```

NetBird 预检：

```powershell
python scripts/netbird_preflight.py
```

最小检索验证：

```powershell
python scripts/retrieve_kb.py "太空舱" --top-k 1
```

## 常见问题

### `未找到 NetBird CLI`

安装 NetBird 客户端，或确认 `C:\Program Files\NetBird\netbird.exe` 存在。

### `Wrong NetBird server` 或 `NetBird 服务器不正确`

当前 NetBird Profile 连接的不是自托管服务器。切换到正确 Profile 后重新执行脚本。

### `NetBird 会话已过期`

打开 NetBird 客户端重新登录。

### 检索返回 401 或登录失败

检查 `KB_USERNAME` 和 `KB_PASSWORD` 是否正确，确认终端和 Codex 已重新加载环境变量。

### 提示找不到知识库

`--kb-name` 必须和 AstrBot 中的知识库名称完全一致。先用 AstrBot WebUI 或 `/api/kb/list` 确认名称。

### 上传长时间没有完成

AstrBot 后台可能仍在解析、分块或向量化。脚本最多等待 15 分钟；embedding 服务不可用或文档异常时会更早失败。

## 安全要求

- 不要提交 `.env`。
- 默认账号密码是为了让内网用户开箱即用而固定在仓库中的。
- 如果仓库公开或 NetBird 边界变化，应立即轮换 AstrBot 密码，并改回环境变量注入。
- 不要在日志或提交信息中写入更高权限的真实密码和 JWT。
- 预检失败时不要绕过 NetBird 或改用公网地址。

## 当前边界

- 上传脚本面向 AstrBot Dashboard API；它会等待知识库处理完成，但不会自动删除旧版同名文档。
- 删除远端知识库文档需要使用 AstrBot WebUI 或单独的 API 工具。
- NetBird 预检是安全约束，不能用普通网络连通性测试替代。
