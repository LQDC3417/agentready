# Repoize

一条命令让任何项目对 AI Agent 友好。

自动生成 [AGENTS.md](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)、`CLAUDE.md`、`.cursorrules`、MCP Server 配置、Skill 文件，让 Claude Code、Cursor、Copilot 等 AI 编程助手立即理解你的项目。

## 安装

> 当前 GitHub 仓库已改名为 `repoize`。`repoize` 在 PyPI 上当前可用；本项目尚未发布，请先使用源码安装。

```bash
git clone https://github.com/LQDC3417/repoize.git
cd repoize
pip install -e ".[dev]"
```

安装后使用：

```bash
repoize --help
```

## 快速开始

```bash
# 一键扫描 + 生成所有配置文件
repoize init

# 仅查看项目分析报告
repoize analyze

# 选择性生成指定类型的配置文件
repoize generate --type agents --type mcp

# 检查项目 Agent 就绪度
repoize check

# 增量更新配置，保留手写内容
repoize update

# 输出 JSON 分析结果并校验
repoize analyze --format json --output repoize-analysis.json
repoize validate repoize-analysis.json
```

## 功能

### `repoize init`

扫描项目目录，自动检测语言、框架、依赖、构建命令，然后生成：

- **AGENTS.md** — 通用 Agent 指令文件
- **CLAUDE.md** — Claude Code 专属指令
- **.cursorrules** — Cursor AI 规则文件
- **.github/copilot-instructions.md** — GitHub Copilot 指令
- **.claude/mcp.json** — MCP Server 配置
- **.claude/skills/project-dev/SKILL.md** — 项目专属 Skill 文件

### `repoize analyze`

输出项目健康度报告，包括：

- 语言、语言画像和框架检测
- 依赖信息
- 已有 Agent 配置状态
- 测试和 CI/CD 状态
- 常用命令提取
- 开发环境信息

### `repoize generate`

选择性生成指定类型的配置文件：

```bash
repoize generate --type agents        # 仅生成 AGENTS.md
repoize generate --type claude        # 仅生成 CLAUDE.md
repoize generate --type cursorrules   # 仅生成 .cursorrules
repoize generate --type copilot       # 仅生成 Copilot 指令
repoize generate --type mcp           # 仅生成 MCP 配置
repoize generate --type skill         # 仅生成 Skill 文件
```

### `repoize update`

增量更新已生成的配置文件：

- 缺失的文件会自动创建。
- Markdown/文本文件只替换 `repoize:generated-start` 和 `repoize:generated-end` 之间的内容，区间外的手写内容会保留。
- JSON 文件会合并对象，保留已有但未由 repoize 生成的字段，例如自定义 MCP server。
- 没有 managed marker 的已有文件不会被覆盖。

```bash
# 更新所有配置
repoize update

# 只更新 AGENTS.md 和 MCP 配置
repoize update --type agents --type mcp
```

### `repoize validate`

校验 `repoize analyze --format json` 生成的 JSON 是否符合内置 JSON Schema：

```bash
repoize analyze . --format json --output repoize-analysis.json
repoize validate repoize-analysis.json
```

JSON Schema 位于 `src/repoize/schemas/analysis.schema.json`，可用于 GitHub Actions、GitLab CI 或其他 CI 系统对分析结果做一致性校验。

### `repoize check`

检查项目是否已具备 Agent 友好配置，并给出改进建议。

## 支持的语言

| 语言 | 分析深度 | 生成质量 |
|------|---------|---------|
| **Python** | 完整 | 高 |
| **JavaScript** | 基础 | 中 |
| **TypeScript** | 基础 | 中 |
| **Go** | 基础 | 中 |
| **Rust** | 基础 | 中 |
| **Java** | 基础 | 中 |
| **Ruby** | 基础 | 中 |
| **PHP** | 基础 | 中 |
| **其他** | 文件检测 | 基础 |

## 设计特点

- 纯本地分析，不调用 AI 模型，不依赖外部 API。
- 敏感环境变量自动过滤，避免把 key、token、password 等写入生成文档。
- 语言 profile 驱动模板，不同语言生成对应的安装、构建、测试和 lint 命令。
- 一个 CLI 同时维护 Claude Code、Cursor、GitHub Copilot、MCP 和 Skill 配置。
- 增量更新会保留手写内容，JSON 输出带 Schema 可供 CI 校验。

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check src/ tests/

# 格式检查
ruff format --check src/ tests/
```

## License

MIT
