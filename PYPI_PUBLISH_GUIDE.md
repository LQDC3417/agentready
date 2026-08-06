# PyPI 发布指南

## 📋 发布前检查清单

- [x] 代码已提交并推送到GitHub
- [x] README.md 已更新（中英文双语、徽章、安装说明）
- [x] CHANGELOG.md 已创建
- [x] pyproject.toml 配置正确
- [x] 包已构建并通过 twine check

## 🚀 发布步骤

### 步骤 1: 创建 PyPI 账号

1. 访问 https://pypi.org/account/register/ 注册账号
2. 验证邮箱

### 步骤 2: 创建 API Token

1. 登录 PyPI: https://pypi.org/manage/account/
2. 进入 "API tokens" 页面: https://pypi.org/manage/account/token/
3. 点击 "Add API token"
4. 设置 Token 名称（如 "repoize-publish"）
5. 选择 "Entire account" 或指定项目
6. **复制并保存 Token**（只显示一次！）

### 步骤 3: 配置 Token

**方法 1: 使用环境变量（推荐）**

```powershell
# Windows PowerShell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-你的API-Token"
```

```bash
# Linux/macOS
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-你的API-Token"
```

**方法 2: 使用 ~/.pypirc 文件**

创建文件 `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-你的API-Token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-你的TestPyPI-Token
```

### 步骤 4: 发布

**方法 1: 使用发布脚本（推荐）**

```powershell
.\publish_to_pypi.ps1
```

**方法 2: 手动发布**

```bash
# 构建
python -m build

# 检查
twine check dist/*

# 上传到 TestPyPI（先测试）
twine upload --repository testpypi dist/*

# 上传到 PyPI（正式发布）
twine upload dist/*
```

### 步骤 5: 验证发布

1. 访问 https://pypi.org/project/repoize/
2. 测试安装: `pip install repoize`
3. 测试命令: `repoize --help`

## 🧪 先测试再发布（推荐）

### 1. 上传到 TestPyPI

```bash
# 创建 TestPyPI 账号: https://test.pypi.org/account/register/
# 创建 TestPyPI API Token

# 上传
twine upload --repository testpypi dist/*
```

### 2. 从 TestPyPI 安装测试

```bash
pip install --index-url https://test.pypi.org/simple/ repoize
```

### 3. 验证功能

```bash
repoize --help
repoize analyze --no-env
```

### 4. 确认无误后上传到正式 PyPI

```bash
twine upload dist/*
```

## 📦 发布后更新

当需要发布新版本时：

1. 更新 `pyproject.toml` 中的版本号
2. 更新 `CHANGELOG.md`
3. 提交并推送代码
4. 重新构建并上传

```bash
# 更新版本号（例如从 0.1.0 到 0.2.0）
# 编辑 pyproject.toml: version = "0.2.0"

# 构建新版本
python -m build

# 上传
twine upload dist/*
```

## ❓ 常见问题

### Q: 上传失败 "403 Forbidden"
A: 检查 Token 是否正确，确保使用 `__token__` 作为用户名

### Q: 上传失败 "400 Bad Request"
A: 检查版本号是否已存在，PyPI 不允许重复上传相同版本

### Q: 如何删除已发布的版本？
A: PyPI 不允许删除已发布的版本，只能发布新版本覆盖

### Q: 如何查看下载统计？
A: 访问 https://pepy.tech/project/repoize

## 📚 相关资源

- [PyPI 官方文档](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Twine 文档](https://twine.readthedocs.io/)
- [TestPyPI](https://test.pypi.org/)
- [PyPI 下载统计](https://pepy.tech/)
