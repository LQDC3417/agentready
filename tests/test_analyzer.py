"""项目分析器 + 配置扫描器测试"""

import tempfile
from pathlib import Path

from agentready.analyzer.project_analyzer import analyze_project
from agentready.analyzer.config_scanner import scan_existing_configs


def test_analyze_with_env():
    """测试带环境扫描的分析。"""
    tmp = Path(tempfile.mkdtemp())
    (tmp / "main.py").write_text("print('hi')", encoding="utf-8")
    analysis = analyze_project(tmp, scan_env=True)
    assert analysis.env_info.system  # 应有系统信息
    assert len(analysis.env_info.tools) > 0  # 应检测到工具


def test_analyze_without_env():
    """测试不带环境扫描的分析。"""
    tmp = Path(tempfile.mkdtemp())
    (tmp / "main.py").write_text("print('hi')", encoding="utf-8")
    analysis = analyze_project(tmp, scan_env=False)
    assert analysis.env_info.system == ""  # 应为空


def test_config_scanner_detects_claude_md(tmp_path):
    """测试配置扫描器检测 CLAUDE.md。"""
    (tmp_path / "CLAUDE.md").write_text("# test", encoding="utf-8")
    configs = scan_existing_configs(tmp_path)
    claude_cfg = next(c for c in configs if c.config_type == "claude_md")
    assert claude_cfg.exists is True


def test_config_scanner_missing_claude_md(tmp_path):
    """测试配置扫描器检测缺失的 CLAUDE.md。"""
    configs = scan_existing_configs(tmp_path)
    claude_cfg = next(c for c in configs if c.config_type == "claude_md")
    assert claude_cfg.exists is False


def test_analyze_empty_project(tmp_path):
    """测试空项目分析。"""
    analysis = analyze_project(tmp_path, scan_env=False)
    assert analysis.primary_language is None
    assert len(analysis.dependencies) == 0
    assert analysis.has_tests is False
    assert analysis.has_ci is False
    assert analysis.agent_ready_score == 0


def test_analyze_multi_language(tmp_path):
    """测试多语言项目检测。"""
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")
    (tmp_path / "app.py").write_text("print('app')", encoding="utf-8")
    (tmp_path / "index.js").write_text("console.log('hi')", encoding="utf-8")
    analysis = analyze_project(tmp_path, scan_env=False)
    assert analysis.primary_language == "Python"
    assert "JavaScript" in analysis.languages


def test_analyze_with_ci(tmp_path):
    """测试 CI 配置检测。"""
    (tmp_path / "main.py").write_text("print('hi')", encoding="utf-8")
    workflows = tmp_path / ".github" / "workflows"
    workflows.mkdir(parents=True)
    (workflows / "ci.yml").write_text("name: CI", encoding="utf-8")
    analysis = analyze_project(tmp_path, scan_env=False)
    assert analysis.has_ci is True
