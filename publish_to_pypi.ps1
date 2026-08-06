# PyPI 发布脚本
# 使用前请确保已安装 build 和 twine: pip install build twine

Write-Host "=== Repoize PyPI 发布脚本 ===" -ForegroundColor Cyan
Write-Host ""

# 1. 清理旧的构建文件
Write-Host "[1/4] 清理旧的构建文件..." -ForegroundColor Yellow
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" }
if (Test-Path "build") { Remove-Item -Recurse -Force "build" }
if (Test-Path "*.egg-info") { Remove-Item -Recurse -Force "*.egg-info" }

# 2. 构建包
Write-Host "[2/4] 构建包..." -ForegroundColor Yellow
python -m build
if ($LASTEXITCODE -ne 0) {
    Write-Host "构建失败！" -ForegroundColor Red
    exit 1
}

# 3. 检查包
Write-Host "[3/4] 检查包..." -ForegroundColor Yellow
twine check dist/*
if ($LASTEXITCODE -ne 0) {
    Write-Host "包检查失败！" -ForegroundColor Red
    exit 1
}

# 4. 上传到PyPI
Write-Host "[4/4] 上传到PyPI..." -ForegroundColor Yellow
Write-Host ""
Write-Host "请选择上传目标:" -ForegroundColor Cyan
Write-Host "  1. TestPyPI (测试环境，推荐先测试)" -ForegroundColor White
Write-Host "  2. PyPI (正式环境)" -ForegroundColor White
Write-Host ""
$choice = Read-Host "请输入选项 (1 或 2)"

if ($choice -eq "1") {
    Write-Host "上传到 TestPyPI..." -ForegroundColor Yellow
    twine upload --repository testpypi dist/*
} elseif ($choice -eq "2") {
    Write-Host "上传到 PyPI..." -ForegroundColor Yellow
    twine upload dist/*
} else {
    Write-Host "无效选项，退出" -ForegroundColor Red
    exit 1
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=== 发布成功！===" -ForegroundColor Green
    Write-Host ""
    Write-Host "安装命令:" -ForegroundColor Cyan
    Write-Host "  pip install repoize" -ForegroundColor White
    Write-Host ""
    Write-Host "PyPI 页面:" -ForegroundColor Cyan
    Write-Host "  https://pypi.org/project/repoize/" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "=== 发布失败 ===" -ForegroundColor Red
    Write-Host "请检查API Token是否正确" -ForegroundColor Yellow
}
