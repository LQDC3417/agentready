"""生成器测试"""

import tempfile
from pathlib import Path

from agentready.analyzer.project_analyzer import analyze_project
from agentready.generator.agents_md import AgentsMdGenerator
from agentready.generator.claude_md import ClaudeMdGenerator
from agentready.generator.copilot import CopilotGenerator
from agentready.generator.cursorrules import CursorRulesGenerator
from agentready.generator.mcp_config import McpConfigGenerator
from agentready.generator.skill_md import SkillMdGenerator


def _make_analysis():
    """创建测试用的分析结果。"""
    tmp = Path(tempfile.mkdtemp())
    (tmp / "main.py").write_text("print('hello')", encoding="utf-8")
    (tmp / "pyproject.toml").write_text(
        """[project]
name = "test-project"
dependencies = ["fastapi>=0.100", "uvicorn"]
[project.optional-dependencies]
dev = ["pytest"]
[project.scripts]
test-app = "app.main:main"
""",
        encoding="utf-8",
    )
    (tmp / "tests").mkdir()
    (tmp / "tests" / "test_main.py").write_text("def test_ok(): pass", encoding="utf-8")
    return analyze_project(tmp, scan_env=False)


def test_agents_md_generator():
    """测试 AGENTS.md 生成器。"""
    analysis = _make_analysis()
    gen = AgentsMdGenerator(analysis)
    content = gen.generate()
    assert analysis.project_name in content
    assert "Python" in content
    assert "fastapi" in content
    assert "pytest" in content
    assert gen.output_filename == "AGENTS.md"


def test_claude_md_generator():
    """测试 CLAUDE.md 生成器。"""
    analysis = _make_analysis()
    gen = ClaudeMdGenerator(analysis)
    content = gen.generate()
    assert "Claude Code" in content
    assert analysis.project_name in content
    assert "Python" in content
    assert "fastapi" in content
    assert "编码规范" in content
    assert "工作流程" in content
    assert gen.output_filename == "CLAUDE.md"


def test_cursorrules_generator():
    """测试 .cursorrules 生成器。"""
    analysis = _make_analysis()
    gen = CursorRulesGenerator(analysis)
    content = gen.generate()
    assert "Cursor Rules" in content
    assert "pytest" in content
    assert gen.output_filename == ".cursorrules"


def test_copilot_generator():
    """测试 copilot-instructions 生成器。"""
    analysis = _make_analysis()
    gen = CopilotGenerator(analysis)
    content = gen.generate()
    assert "Copilot" in content
    assert gen.output_filename == ".github/copilot-instructions.md"


def test_mcp_config_generator():
    """测试 MCP 配置生成器。"""
    analysis = _make_analysis()
    gen = McpConfigGenerator(analysis)
    content = gen.generate()
    assert "mcpServers" in content
    assert "git" in content
    assert gen.output_filename == ".claude/mcp.json"


def test_skill_md_generator():
    """测试 SKILL.md 生成器。"""
    analysis = _make_analysis()
    gen = SkillMdGenerator(analysis)
    content = gen.generate()
    assert analysis.project_name in content
    assert gen.output_filename == ".claude/skills/project-dev/SKILL.md"


def test_generator_write(tmp_path):
    """测试生成器写入文件。"""
    analysis = _make_analysis()
    gen = AgentsMdGenerator(analysis)
    result_path = gen.write(tmp_path)
    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert analysis.project_name in content


def test_generator_write_conflict(tmp_path):
    """测试生成器文件冲突检测。"""
    analysis = _make_analysis()
    gen = AgentsMdGenerator(analysis)
    gen.write(tmp_path)
    import pytest

    with pytest.raises(FileExistsError):
        gen.write(tmp_path, force=False)


def test_generator_write_force(tmp_path):
    """测试 --force 覆盖写入。"""
    analysis = _make_analysis()
    gen = AgentsMdGenerator(analysis)
    gen.write(tmp_path)
    gen.write(tmp_path, force=True)


def test_dep_parser_no_scripts():
    """测试依赖解析不包含 scripts 条目。"""
    analysis = _make_analysis()
    dep_names = [d.name for d in analysis.dependencies]
    # app.main:main 是 scripts 条目，不应出现在依赖中
    assert "app.main:main" not in dep_names
    assert "fastapi" in dep_names
    assert "uvicorn" in dep_names
    assert "pytest" in dep_names


def test_template_no_bom():
    """测试模板文件不含 BOM。"""
    from jinja2 import Environment, FileSystemLoader

    template_dir = Path(__file__).parent.parent / "src" / "agentready" / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    for name in ["agents_md.j2", "claude_md.j2", "cursorrules.j2", "copilot.j2", "mcp_config.j2", "skill_md.j2"]:
        source, _, _ = env.loader.get_source(env, name)
        assert not source.startswith("\ufeff"), f"{name} contains BOM"
