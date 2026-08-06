"""代码质量分析器测试"""

import tempfile
from pathlib import Path

from repoize.analyzer.quality_analyzer import analyze_code_quality


def test_analyze_code_quality_empty_project():
    """测试空项目的代码质量分析。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        metrics = analyze_code_quality(project_path)

        assert metrics.total_files == 0
        assert metrics.total_lines == 0
        assert metrics.code_lines == 0


def test_analyze_code_quality_python_project():
    """测试Python项目的代码质量分析。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # 创建一个简单的Python文件
        py_file = project_path / "test.py"
        py_file.write_text('''def hello():
    """Say hello."""
    print("Hello, World!")

def add(a, b):
    """Add two numbers."""
    return a + b
''')

        metrics = analyze_code_quality(project_path)

        assert metrics.total_files == 1
        assert metrics.total_lines > 0
        assert metrics.files_by_language.get("Python") == 1


def test_analyze_code_quality_with_config():
    """测试有配置文件的代码质量分析。"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # 创建配置文件
        config_file = project_path / ".flake8"
        config_file.write_text("[flake8]\nmax-line-length = 120\n")

        metrics = analyze_code_quality(project_path)

        assert ".flake8" in metrics.quality_config_found
