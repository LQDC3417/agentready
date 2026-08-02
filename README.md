# Agent-Ready

一条命令让任何项目对 AI Agent 友好。

自动生成 [AGENTS.md](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)、`CLAUDE.md`、`.cursorrules`、MCP Server 配置、Skill 文件，让 Claude Code、Cursor、Copilot 等 AI 编程助手立即理解你的项目。

## 安装

> 注意：PyPI 上的 `agentready` 包名已被其他项目占用，本项目当前尚未发布到 PyPI，请使用源码安装。

```bash
git clone https://github.com/LQDC3417/agentready.git
cd agentready
pip install -e ".[dev]"
```

安装后使用：

```bash
agentready --help
```

## 快速开始

```bash
# 一键扫描 + 生成所有配置文件
agentready init

# 仅查看项目分析报告
agentready analyze

# 选择性生成指定类型的配置文件
agentready generate --type agents --type mcp

# 检查项目 Agent 就绪度
agentready check
```

## 功能

### `agentready init`

扫描项目目录，自动检测语言、框架、依赖、构建命令，然后生成：

- **AGENTS.md** — 通用 Agent 指令文件
- **CLAUDE.md** — Claude Code 专属指令
- **.cursorrules** — Cursor AI 规则文件
- **.github/copilot-instructions.md** — GitHub Copilot 指令
- **.claude/mcp.json** — MCP Server 配置
- **.claude/skills/project-dev/SKILL.md** — 项目专属 Skill 文件

### `agentready analyze`

输出项目健康度报告，包括：

- 语言、语言画像和框架检测
- 依赖信息
- 已有 Agent 配置状态
- 测试和 CI/CD 状态
- 常用命令提取
- 开发环境信息

### `agentready generate`

选择性生成指定类型的配置文件：

```bash
agentready generate --type agents        # 仅生成 AGENTS.md
agentready generate --type claude        # 仅生成 CLAUDE.md
agentready generate --type cursorrules   # 仅生成 .cursorrules
agentready generate --type copilot       # 仅生成 Copilot 指令
agentready generate --type mcp           # 仅生成 MCP 配置
agentready generate --type skill         # 仅生成 Skill 文件
```

### `agentready check`

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
