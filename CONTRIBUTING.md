# 贡献指南

感谢您对 Repoize 项目的关注！我们欢迎各种形式的贡献。

## 开发环境设置

### 前置要求

- Python 3.10+
- Git

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/LQDC3417/repoize.git
cd repoize

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

# 安装开发依赖
pip install -e ".[dev]"
```

## 开发流程

### 1. 创建分支

```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

### 2. 编写代码

- 遵循项目代码规范（PEP 8）
- 添加类型注解
- 编写中文注释（技术术语保留英文）
- 保持函数简洁（建议 < 50 行）

### 3. 编写测试

```bash
# 运行测试
pytest

# 运行测试并查看覆盖率
pytest --cov=src/repoize --cov-report=term-missing
```

### 4. 代码质量检查

```bash
# Lint 检查
ruff check src tests

# 格式检查
ruff format --check src tests

# 自动修复格式问题
ruff format src tests
```

### 5. 提交代码

```bash
git add .
git commit -m "feat: 添加新功能描述"
# 或
git commit -m "fix: 修复某个问题"
```

**提交信息规范：**
- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具链更新

### 6. 推送并创建 PR

```bash
git push origin feature/your-feature-name
```

然后在 GitHub 上创建 Pull Request。

## 代码规范

### Python 代码

```python
"""模块文档字符串"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from some.module import SomeType


def function_name(param: str, optional: int = 0) -> dict[str, Any]:
    """函数文档字符串。
    
    Args:
        param: 参数说明
        optional: 可选参数说明
    
    Returns:
        返回值说明
    """
    # 关键逻辑添加注释
    result = do_something(param)
    return {"result": result}
```

### 测试代码

```python
"""测试模块"""

import pytest
from pathlib import Path

from repoize.module import function_name


def test_function_name_basic():
    """测试基本功能。"""
    result = function_name("test")
    assert result["result"] == "expected"


def test_function_name_edge_case(tmp_path):
    """测试边界情况。"""
    # 测试代码
    pass
```

## 报告问题

使用 GitHub Issues 报告问题，请包含：

1. **问题描述**：清晰简洁地描述问题
2. **复现步骤**：如何触发问题
3. **期望行为**：您期望发生什么
4. **实际行为**：实际发生了什么
5. **环境信息**：
   - 操作系统
   - Python 版本
   - Repoize 版本

## 功能建议

欢迎提出功能建议！请在 Issue 中说明：

1. **使用场景**：为什么需要这个功能
2. **期望实现**：您希望如何工作
3. **替代方案**：您目前如何解决这个问题

## 发布流程

维护者发布新版本的流程：

1. 更新 `CHANGELOG.md`
2. 更新 `pyproject.toml` 中的版本号
3. 创建 Git Tag
4. 推送到 GitHub
5. 在 PyPI 上发布

```bash
# 更新版本号
# 编辑 pyproject.toml: version = "x.y.z"

# 提交并打标签
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to x.y.z"
git tag vx.y.z
git push origin main --tags

# 发布到 PyPI
python -m build
twine upload dist/*
```

## 行为准则

- 尊重所有参与者
- 接受建设性批评
- 专注于对社区最有利的事情
- 对他人表示同理心

## 许可证

贡献即表示您同意您的代码将在 MIT 许可证下发布。

---

如有任何问题，请在 GitHub Issues 中提问。
