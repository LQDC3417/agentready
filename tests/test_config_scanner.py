"""配置扫描器测试"""

from pathlib import Path

from repoize.analyzer.config_scanner import (
    ConfigStatus,
    has_any_agent_config,
    scan_existing_configs,
)


def test_config_status_init():
    """测试 ConfigStatus 初始化。"""
    status = ConfigStatus(
        name="CLAUDE.md",
        config_type="claude_md",
        exists=True,
        path=Path("/test/CLAUDE.md"),
    )
    assert status.name == "CLAUDE.md"
    assert status.config_type == "claude_md"
    assert status.exists is True
    assert status.path == Path("/test/CLAUDE.md")


def test_config_status_repr_exists():
    """测试 ConfigStatus 字符串表示（存在）。"""
    status = ConfigStatus(
        name="CLAUDE.md",
        config_type="claude_md",
        exists=True,
        path=Path("/test/CLAUDE.md"),
    )
    repr_str = repr(status)
    assert "✅" in repr_str
    assert "CLAUDE.md" in repr_str


def test_config_status_repr_not_exists():
    """测试 ConfigStatus 字符串表示（不存在）。"""
    status = ConfigStatus(
        name="CLAUDE.md",
        config_type="claude_md",
        exists=False,
        path=Path("/test/CLAUDE.md"),
    )
    repr_str = repr(status)
    assert "❌" in repr_str
    assert "CLAUDE.md" in repr_str


def test_config_status_to_dict():
    """测试 ConfigStatus 转换为字典。"""
    status = ConfigStatus(
        name="CLAUDE.md",
        config_type="claude_md",
        exists=True,
        path=Path("/test/CLAUDE.md"),
    )
    result = status.to_dict()
    assert result["name"] == "CLAUDE.md"
    assert result["config_type"] == "claude_md"
    assert result["exists"] is True
    assert "CLAUDE.md" in result["path"]


def test_scan_existing_configs_empty(tmp_path):
    """测试扫描空目录。"""
    configs = scan_existing_configs(tmp_path)
    assert len(configs) > 0
    assert all(not cfg.exists for cfg in configs)


def test_scan_existing_configs_with_agents_md(tmp_path):
    """测试扫描包含 AGENTS.md 的目录。"""
    (tmp_path / "AGENTS.md").write_text("# Agents", encoding="utf-8")
    configs = scan_existing_configs(tmp_path)
    agents_config = next(cfg for cfg in configs if cfg.name == "AGENTS.md")
    assert agents_config.exists is True


def test_scan_existing_configs_with_claude_md(tmp_path):
    """测试扫描包含 CLAUDE.md 的目录。"""
    (tmp_path / "CLAUDE.md").write_text("# Claude", encoding="utf-8")
    configs = scan_existing_configs(tmp_path)
    claude_config = next(cfg for cfg in configs if cfg.name == "CLAUDE.md")
    assert claude_config.exists is True


def test_scan_existing_configs_with_cursorrules(tmp_path):
    """测试扫描包含 .cursorrules 的目录。"""
    (tmp_path / ".cursorrules").write_text("# Cursor Rules", encoding="utf-8")
    configs = scan_existing_configs(tmp_path)
    cursor_config = next(cfg for cfg in configs if cfg.name == ".cursorrules")
    assert cursor_config.exists is True


def test_scan_existing_configs_with_copilot(tmp_path):
    """测试扫描包含 Copilot 配置的目录。"""
    (tmp_path / ".github").mkdir()
    (tmp_path / ".github" / "copilot-instructions.md").write_text("# Copilot", encoding="utf-8")
    configs = scan_existing_configs(tmp_path)
    copilot_config = next(cfg for cfg in configs if cfg.name == ".github/copilot-instructions.md")
    assert copilot_config.exists is True


def test_scan_existing_configs_with_claude_skills(tmp_path):
    """测试扫描包含 Claude skills 的目录。"""
    (tmp_path / ".claude" / "skills" / "test-skill").mkdir(parents=True)
    (tmp_path / ".claude" / "skills" / "test-skill" / "SKILL.md").write_text("# Skill", encoding="utf-8")
    configs = scan_existing_configs(tmp_path)
    skill_configs = [cfg for cfg in configs if cfg.config_type == "skill_claude"]
    assert len(skill_configs) > 0
    assert all(cfg.exists for cfg in skill_configs)


def test_has_any_agent_config_true(tmp_path):
    """测试 has_any_agent_config 返回 True。"""
    (tmp_path / "CLAUDE.md").write_text("# Claude", encoding="utf-8")
    assert has_any_agent_config(tmp_path) is True


def test_has_any_agent_config_false(tmp_path):
    """测试 has_any_agent_config 返回 False。"""
    assert has_any_agent_config(tmp_path) is False
