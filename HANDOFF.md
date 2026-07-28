# HANDOFF.md - 项目交接文档

> 本文件供新 session 加载，快速了解项目全貌和当前进度。
> 新会话时请先读取此文件。

## 项目概述

- 项目名: agentready
- 仓库: https://github.com/LQDC3417/agentready
- 功能: 一条命令让任何项目对 AI Agent 友好 - 自动生成 AGENTS.md、CLAUDE.md、.cursorrules、MCP 配置、Skill 文件
- 技术栈: Python 3.10+ / click / rich / jinja2
- 构建后端: hatchling
- 代码规范: ruff (lint + format)
- CI: GitHub Actions (lint + 多版本测试 3.10-3.13)

## 项目结构

```
src/agentready/
  cli.py                    CLI 入口 (click 命令组)
  analyzer/
    lang_detector.py        语言检测 (30+ 语言)
    dep_parser.py           依赖解析 (pyproject/package.json/go.mod/Cargo.toml)
    cmd_extractor.py        构建/测试/lint 命令提取
    config_scanner.py       已有 Agent 配置扫描
    env_scanner.py          系统环境变量扫描 (工具版本 + 环境变量)
    project_analyzer.py     主分析器 (协调各子模块)
  generator/
    base.py                 生成器基类
    agents_md.py            AGENTS.md 生成
    claude_md.py            CLAUDE.md 生成
    cursorrules.py          .cursorrules 生成
    copilot.py              copilot-instructions.md 生成
    mcp_config.py           MCP 配置生成
    skill_md.py             SKILL.md 生成
  templates/                Jinja2 模板 (6 个 .j2 文件)
  reporter/
    health_report.py        健度报告 (rich 终端美化)
tests/                      33 个测试全部通过
.github/workflows/ci.yml   GitHub Actions CI
```

## CLI 命令

```bash
agentready init [--force] [--no-env]       一键生成所有配置文件
agentready analyze [--no-env]              仅输出项目分析报告
agentready generate --type <type>          选择性生成 (agents/claude/cursorrules/copilot/mcp/skill)
agentready check                           检查 Agent 就绪度
```

## 开发命令

```bash
pip install -e ".[dev]"                     安装开发依赖
python -m pytest tests/ -v                 运行测试
ruff check src/ tests/                     代码检查
ruff format --check src/ tests/            格式检查
ruff check src/ tests/ --fix               自动修复 lint
ruff format src/ tests/                    自动格式化
```

## 已完成

- [x] 项目骨架 (pyproject.toml + src 布局 + click CLI)
- [x] 分析引擎: 语言检测、依赖解析、命令提取、配置扫描
- [x] 环境变量扫描器 (工具版本检测 + 环境变量过滤敏感信息)
- [x] 6 个生成器 (AGENTS.md、CLAUDE.md、.cursorrules、copilot-instructions、MCP config、SKILL.md)
- [x] 健度报告 (终端美化输出)
- [x] ruff 代码规范配置
- [x] GitHub Actions CI (lint + 多版本测试)
- [x] 33 个测试全部通过

## 待完成

- [ ] HTML 报告输出 (analyze --format html 当前是占位)
- [ ] 多语言模板优化 (JS/Go/Rust 生成器模板当前只有基础支持)
- [ ] 覆盖率报告 (pytest-cov 目标 70%+)
- [ ] CHANGELOG.md 版本变更记录
- [ ] PyPI 发布配置
- [ ] 清理已合并分支: feat/env-scan-and-claude-md 和 feat/ci-and-ruff

## 关键设计决策

1. 不依赖 AI 模型 - 纯本地分析 + 模板生成零成本使用
2. 使用 click 而非 typer - click 更成熟且无额外依赖
3. 使用 Jinja2 做模板引擎 - 模板较复杂且需要条件逻辑
4. 动态加载生成器 - cli.py 通过 GENERATOR_MAP 动态导入新增生成器只需添加映射
5. 环境扫描可选 - 通过 --no-env 参数跳过保护隐私

## Git 状态

- 当前在 main 分支
- 最新提交: 135dbb2 Merge branch feat/ci-and-ruff
- 两个已合并的 feature 分支可删除

## 下次开发时

1. 加载本文件了解项目状态
2. git pull 同步远程最新代码
3. python -m pytest tests/ -v 确认测试通过
4. 选择待完成功能继续开发