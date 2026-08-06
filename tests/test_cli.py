"""CLI 模块测试"""

import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from repoize.cli import main


@pytest.fixture
def runner():
    """创建 CLI 测试运行器。"""
    return CliRunner()


@pytest.fixture
def sample_project(tmp_path):
    """创建示例项目目录。"""
    # 创建一个简单的 Python 项目
    (tmp_path / "pyproject.toml").write_text("""
[project]
name = "test-project"
version = "0.1.0"
""")
    (tmp_path / "main.py").write_text("print('Hello, World!')")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test_hello(): pass")
    return tmp_path


def test_main_help(runner):
    """测试主命令帮助信息。"""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "repoize" in result.output
    assert "一条命令让任何项目对 AI Agent 友好" in result.output


def test_analyze_help(runner):
    """测试 analyze 命令帮助信息。"""
    result = runner.invoke(main, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "分析项目结构" in result.output


def test_generate_help(runner):
    """测试 generate 命令帮助信息。"""
    result = runner.invoke(main, ["generate", "--help"])
    assert result.exit_code == 0
    assert "选择性生成指定类型的配置文件" in result.output


def test_check_help(runner):
    """测试 check 命令帮助信息。"""
    result = runner.invoke(main, ["check", "--help"])
    assert result.exit_code == 0
    assert "检查项目是否已具备 Agent 友好配置" in result.output


def test_validate_help(runner):
    """测试 validate 命令帮助信息。"""
    result = runner.invoke(main, ["validate", "--help"])
    assert result.exit_code == 0
    assert "校验" in result.output


def test_analyze_json_output(runner, sample_project):
    """测试 analyze 命令 JSON 输出。"""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        output_file = f.name

    try:
        result = runner.invoke(
            main, ["analyze", str(sample_project), "--format", "json", "--output", output_file, "--no-env"]
        )
        assert result.exit_code == 0
        assert "✅ 已写入" in result.output

        # 验证输出文件存在
        assert Path(output_file).exists()
    finally:
        Path(output_file).unlink(missing_ok=True)


def test_analyze_terminal_output(runner, sample_project):
    """测试 analyze 命令终端输出。"""
    result = runner.invoke(main, ["analyze", str(sample_project), "--format", "terminal", "--no-env"])
    assert result.exit_code == 0
    assert "📊 项目健康度报告" in result.output


def test_generate_missing_types(runner, sample_project):
    """测试 generate 命令缺少类型参数。"""
    result = runner.invoke(main, ["generate", str(sample_project)])
    assert result.exit_code == 1
    assert "请至少指定一个文件类型" in result.output


def test_generate_with_type(runner, sample_project):
    """测试 generate 命令指定类型。"""
    result = runner.invoke(main, ["generate", str(sample_project), "--type", "agents", "--no-env"])
    assert result.exit_code == 0
    assert "✅ 生成 AGENTS.md" in result.output


def test_check_command(runner, sample_project):
    """测试 check 命令。"""
    result = runner.invoke(main, ["check", str(sample_project)])
    assert result.exit_code == 0
    assert "📊 项目健康度报告" in result.output
