---
name: git-proj
description: |-
  项目 git_proj 的开发指南。包含构建、测试、部署的标准流程和编码规范。
license: MIT
---

# git_proj 开发指南

## 快速开始

```bash
# 安装依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码检查
# 未检测到 lint 工具
```


## 项目结构

- 主语言: Python
- 依赖: click
- 依赖: rich
- 依赖: jinja2


## 编码规范

1. 代码注释使用中文，变量名和函数名使用英文
2. 遵循项目已有代码风格
3. 修改代码前先理解现有逻辑
4. 关键逻辑加注释，简单代码不加注释
5. 能用 50 行写完就不要写 200 行

## 常用命令

### 测试
- `pytest`
