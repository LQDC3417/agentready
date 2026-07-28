"""CLI 端到端测试"""

from click.testing import CliRunner
from agentready.cli import main


def test_main_help():
    """测试 CLI 帮助信息。"""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "agentready" in result.output


def test_analyze_help():
    """测试 analyze 子命令帮助。"""
    runner = CliRunner()
    result = runner.invoke(main, ["analyze", "--help"])
    assert result.exit_code == 0
    assert "分析项目" in result.output


def test_init_help():
    """测试 init 子命令帮助。"""
    runner = CliRunner()
    result = runner.invoke(main, ["init", "--help"])
    assert result.exit_code == 0
    assert "扫描项目" in result.output


def test_generate_help():
    """测试 generate 子命令帮助。"""
    runner = CliRunner()
    result = runner.invoke(main, ["generate", "--help"])
    assert result.exit_code == 0
    assert "--type" in result.output


def test_check_help():
    """测试 check 子命令帮助。"""
    runner = CliRunner()
    result = runner.invoke(main, ["check", "--help"])
    assert result.exit_code == 0
    assert "检查" in result.output
