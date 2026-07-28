"""依赖解析器测试"""

from pathlib import Path

from agentready.analyzer.dep_parser import parse_dependencies


def test_parse_pyproject(tmp_path):
    """测试 pyproject.toml 解析。"""
    content = """[project]
name = "test"
dependencies = [
    "click>=8.0",
    "rich>=13.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
]
"""
    (tmp_path / "pyproject.toml").write_text(content, encoding="utf-8")
    deps = parse_dependencies(tmp_path)

    names = [d.name for d in deps]
    assert "click" in names
    assert "rich" in names
    assert "pytest" in names

    pytest_dep = next(d for d in deps if d.name == "pytest")
    assert pytest_dep.dev is True


def test_parse_requirements(tmp_path):
    """测试 requirements.txt 解析。"""
    content = """click>=8.0
rich>=13.0
# comment
-e git+https://...
"""
    (tmp_path / "requirements.txt").write_text(content, encoding="utf-8")
    deps = parse_dependencies(tmp_path)

    names = [d.name for d in deps]
    assert "click" in names
    assert "rich" in names
