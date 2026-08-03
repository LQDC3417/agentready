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


def test_generate_creates_specified_file(tmp_path):
    """测试 generate --type agents 只生成 AGENTS.md。"""
    runner = CliRunner()
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")

    result = runner.invoke(main, ["generate", str(tmp_path), "--type", "agents", "--no-env"])
    assert result.exit_code == 0
    assert (tmp_path / "AGENTS.md").exists()
    # 其他文件不应被创建
    assert not (tmp_path / "CLAUDE.md").exists()
    assert not (tmp_path / ".cursorrules").exists()


def test_generate_multiple_types(tmp_path):
    """测试 generate 同时指定多个类型。"""
    runner = CliRunner()
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")

    result = runner.invoke(main, ["generate", str(tmp_path), "--type", "agents", "--type", "mcp", "--no-env"])
    assert result.exit_code == 0
    assert (tmp_path / "AGENTS.md").exists()
    assert (tmp_path / ".claude" / "mcp.json").exists()


def test_generate_requires_type(tmp_path):
    """测试 generate 不指定 --type 时报错退出。"""
    runner = CliRunner()
    result = runner.invoke(main, ["generate", str(tmp_path)])
    assert result.exit_code != 0
    assert "至少指定一个" in result.output


def test_generate_skip_existing(tmp_path):
    """测试 generate 跳过已存在的文件。"""
    runner = CliRunner()
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")

    # 第一次生成
    runner.invoke(main, ["generate", str(tmp_path), "--type", "agents", "--no-env"])
    original = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")

    # 第二次不加 --force，应跳过
    result = runner.invoke(main, ["generate", str(tmp_path), "--type", "agents", "--no-env"])
    assert "跳过" in result.output
    assert (tmp_path / "AGENTS.md").read_text(encoding="utf-8") == original


def test_generate_force_overwrites(tmp_path):
    """测试 generate --force 覆盖已有文件。"""
    runner = CliRunner()
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")

    # 第一次生成
    runner.invoke(main, ["generate", str(tmp_path), "--type", "agents", "--no-env"])
    # 写入手动内容
    agents = tmp_path / "AGENTS.md"
    agents.write_text(agents.read_text(encoding="utf-8") + "\n# manual\n", encoding="utf-8")

    # --force 覆盖
    result = runner.invoke(main, ["generate", str(tmp_path), "--type", "agents", "--force", "--no-env"])
    assert result.exit_code == 0
    content = agents.read_text(encoding="utf-8")
    assert "# manual" not in content


def test_check_command(tmp_path):
    """测试 check 子命令输出 Agent 就绪度评分。"""
    runner = CliRunner()
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")

    result = runner.invoke(main, ["check", str(tmp_path)])
    assert result.exit_code == 0
    # 空项目应显示未配置
    assert "Agent" in result.output


def test_check_with_configs(tmp_path):
    """测试 check 对已有配置文件的项目给出高分。"""
    runner = CliRunner()
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")
    (tmp_path / "AGENTS.md").write_text("# agents", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# claude", encoding="utf-8")
    (tmp_path / ".cursorrules").write_text("# cursor", encoding="utf-8")

    result = runner.invoke(main, ["check", str(tmp_path)])
    assert result.exit_code == 0
    assert "部分就绪" in result.output or "完备" in result.output
