"""CLI 端到端测试"""

from click.testing import CliRunner

from repoize.cli import main


def test_main_help():
    """测试 CLI 帮助信息。"""
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "repoize" in result.output


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


def test_update_help():
    """测试 update 子命令帮助。"""
    runner = CliRunner()
    result = runner.invoke(main, ["update", "--help"])
    assert result.exit_code == 0
    assert "增量更新" in result.output


def test_update_preserves_manual_content(tmp_path):
    """测试 update 命令保留 marker 外的手写内容。"""
    runner = CliRunner()
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")

    result = runner.invoke(main, ["update", str(tmp_path), "--no-env"])
    assert result.exit_code == 0

    agents_path = tmp_path / "AGENTS.md"
    assert agents_path.exists()
    manual = "\n# 手写说明\n"
    agents_path.write_text(agents_path.read_text(encoding="utf-8") + manual, encoding="utf-8")

    result = runner.invoke(main, ["update", str(tmp_path), "--no-env"])
    assert result.exit_code == 0
    assert manual in agents_path.read_text(encoding="utf-8")


def test_analyze_json(tmp_path):
    """测试 analyze --format json 输出。"""
    runner = CliRunner()
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")

    result = runner.invoke(main, ["analyze", str(tmp_path), "--format", "json", "--no-env"])

    assert result.exit_code == 0
    assert '"schema_version": 1' in result.output
    assert '"project_name"' in result.output


def test_analyze_json_output_and_validate(tmp_path):
    """测试 JSON 文件输出和 validate 命令。"""
    runner = CliRunner()
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")
    output_path = tmp_path / "analysis.json"

    result = runner.invoke(
        main,
        ["analyze", str(tmp_path), "--format", "json", "--output", str(output_path), "--no-env"],
    )
    assert result.exit_code == 0
    assert output_path.exists()

    result = runner.invoke(main, ["validate", str(output_path)])
    assert result.exit_code == 0
    assert "校验通过" in result.output


def test_validate_invalid_json(tmp_path):
    """测试 validate 对不符合 schema 的 JSON 返回失败。"""
    runner = CliRunner()
    bad_path = tmp_path / "bad.json"
    bad_path.write_text('{"foo": 1}', encoding="utf-8")

    result = runner.invoke(main, ["validate", str(bad_path)])

    assert result.exit_code != 0
    assert "校验失败" in result.output
