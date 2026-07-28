# Agent-Ready

一条命令让任何项目对 AI Agent 友好。

自动生成 [AGENTS.md](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot)、`.cursorrules`、MCP Server 配置、Skill 文件，让 Claude Code、Cursor、Copilot 等 AI 编程助手立即理解你的项目。

## 安装

```bash
pip install agentready
```

从源码安装：

```bash
git clone https://github.com/user/agentready.git
cd agentready
pip install -e ".[dev]"
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
- **.cursorrules** — Cursor AI 规则文件
- **.github/copilot-instructions.md** — GitHub Copilot 指令
- **.claude/mcp.json** — MCP Server 配置
- **.claude/skills/project-dev/SKILL.md** — 项目专属 Skill 文件

### `agentready analyze`
输出项目健康度报告，包括：
- 语言和框架检测
- 依赖信息
- 已有 Agent 配置状态
- 测试和 CI/CD 状态
- 常用命令提取

### `agentready generate`
选择性生成指定类型的配置文件：
```bash
agentready generate --type agents        # 仅生成 AGENTS.md
agentready generate --type cursorrules   # 仅生成 .cursorrules
agentready generate --type mcp           # 仅生成 MCP 配置
agentready generate --type skill         # 仅生成 Skill 文件
```

### `agentready check`
检查项目是否已具备 Agent 友好配置，并给出改进建议。

## 支持的语言

| 语言 | 分析深度 | 生成质量 |
|------|---------|---------|
| **Python** | 完整 | 高 |
| **JavaScript/TypeScript** | 基础 | 中 |
| **Go** | 基础 | 中 |
| **Rust** | 基础 | 中 |
| **其他** | 文件检测 | 基础 |

## 生成的文件示例

### AGENTS.md
```markdown
# My Project

## 项目概述
- 主语言: Python
- 框架: FastAPI, SQLAlchemy

## 常用命令
### 测试
\```bash
pytest
\```

### 代码检查
\```bash
ruff check .
\```
```

### .cursorrules
```
# 编码规范
- 代码注释使用中文，变量名和函数名使用英文
- 遵循项目已有代码风格
- 提交前运行: pytest
```

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
ruff check .
```

## License

MIT
