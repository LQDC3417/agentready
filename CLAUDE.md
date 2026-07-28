# CLAUDE.md — Claude Code 项目指令

> 本文件由 [agentready](https://github.com/LQDC3417/agentready) 自动生成。Claude Code 会自动读取此文件。

## 项目信息

- 项目名: git_proj
- 主语言: Python

## 技术栈

- click
- rich
- jinja2




## 测试
```bash
pytest
```






## 开发环境

| 工具 | 版本 |
|------|------|
| Python | Python 3.13.5 |
| Python3 | Python 3.13.12 |
| Node.js | v24.14.1 |
| npm | 11.11.0 |
| bun | 1.3.14 |
| Rust (rustc) | rustc 1.96.0 (ac68faa20 2026-05-25) |
| Cargo | cargo 1.96.0 (30a34c682 2026-05-25) |
| Git | git version 2.45.1.windows.1 |
| uv | uv 0.11.14 (3fdfdc7d4 2026-05-12 x86_64-pc-windows-msvc) |
| pip | pip 25.1 from D:\Program Files\Anaconda\Lib\site-packages\pip (python 3.13) |
| conda | conda 25.7.0 |
| mypy | mypy 1.14.1 (compiled: yes) |


### 环境变量

- `CONDA_DEFAULT_ENV`: `base`
- `CONDA_PREFIX`: `D:\Program Files\Anaconda`
- `CUDA_PATH`: `D:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.1`
- `PATH`: `C:\Users\Administrator\.codex\tmp\arg0\codex-arg0riXYp2;C:\Users\Administrator\.codex\packages\standalone\releases\0.144.3-x86_64-pc-windows-msvc\codex-path;D:\Program Files\Anaconda;D:\Program Files\...`
- `PYTHONPATH`: `src`


## 编码规范

- 代码注释使用中文，变量名和函数名使用英文
- 遵循项目已有代码风格，不要随意修改相邻代码的格式
- 修改代码前先理解现有逻辑
- 关键逻辑加注释，简单代码不加注释
- 能用 50 行写完就不要写 200 行
- 优先使用已有的库和工具
- 提交前运行测试和代码检查

## 工作流程

1. 先读懂现有代码再动手修改
2. 改动最小化，不碰无关文件和逻辑
3. 遇到不确定的地方先问用户确认
4. 改完代码后主动跑相关测试验证
5. 不主动 commit，等用户确认后再提交