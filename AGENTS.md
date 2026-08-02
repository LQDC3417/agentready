# git_proj

> 本文件由 [repoize](https://github.com/LQDC3417/repoize) 自动生成，请根据项目实际情况调整。

## 项目概述

- **主语言**: Python

## 技术栈

- click
- rich
- jinja2


## 开发依赖

- pytest
- pytest-cov


## 常用命令

### 测试
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


## 目录结构

```
git_proj/
├── src/          # 源代码
├── tests/        # 测试
└── ...
```

## 编码规范

- 代码注释使用中文，变量名和函数名使用英文
- 遵循项目已有代码风格
- 修改代码前先理解现有逻辑，保持最小化改动
- 提交前运行 lint 和测试确保通过