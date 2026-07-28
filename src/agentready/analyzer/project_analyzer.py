"""主分析器 — 协调各子模块，输出完整项目分析结果"""

from pathlib import Path
from dataclasses import dataclass, field

from .lang_detector import detect_languages, get_primary_language
from .dep_parser import parse_dependencies, DepInfo
from .cmd_extractor import extract_commands, CommandSet
from .config_scanner import scan_existing_configs, ConfigStatus


@dataclass
class ProjectAnalysis:
    """项目分析结果。"""
    project_path: Path
    project_name: str
    languages: dict[str, float] = field(default_factory=dict)
    primary_language: str | None = None
    dependencies: list[DepInfo] = field(default_factory=list)
    commands: CommandSet = field(default_factory=CommandSet)
    existing_configs: list[ConfigStatus] = field(default_factory=list)
    has_tests: bool = False
    test_framework: str | None = None
    has_ci: bool = False

    @property
    def agent_ready_score(self) -> int:
        """Agent 就绪度评分（0-100）。"""
        score = 0
        existing_types = {c.config_type for c in self.existing_configs if c.exists}
        if "agents_md" in existing_types:
            score += 30
        if "cursorrules" in existing_types:
            score += 20
        if "copilot" in existing_types:
            score += 20
        if "mcp_claude" in existing_types or "mcp_desktop" in existing_types:
            score += 20
        if "skill" in existing_types or "skill_claude" in existing_types:
            score += 10
        return score

    @property
    def agent_ready_label(self) -> str:
        s = self.agent_ready_score
        if s >= 80:
            return "完备"
        if s >= 40:
            return "部分就绪"
        return "未配置"


def analyze_project(project_path: Path) -> ProjectAnalysis:
    """执行完整的项目分析。"""
    project_path = Path(project_path).resolve()

    languages = detect_languages(project_path)
    primary = get_primary_language(project_path)
    deps = parse_dependencies(project_path)
    cmds = extract_commands(project_path)
    configs = scan_existing_configs(project_path)

    # 检测测试
    has_tests = False
    test_framework = None
    if cmds.test:
        has_tests = True
        test_cmd = cmds.test[0].lower()
        if "pytest" in test_cmd:
            test_framework = "pytest"
        elif "jest" in test_cmd:
            test_framework = "jest"
        elif "go test" in test_cmd:
            test_framework = "go test"
        elif "cargo test" in test_cmd:
            test_framework = "cargo test"
    elif (project_path / "tests").is_dir() or (project_path / "test").is_dir():
        has_tests = True

    # 检测 CI
    has_ci = any((
        (project_path / ".github" / "workflows").is_dir(),
        (project_path / ".gitlab-ci.yml").exists(),
        (project_path / "Jenkinsfile").exists(),
        (project_path / ".circleci").is_dir(),
    ))

    return ProjectAnalysis(
        project_path=project_path,
        project_name=project_path.name,
        languages=languages,
        primary_language=primary,
        dependencies=deps,
        commands=cmds,
        existing_configs=configs,
        has_tests=has_tests,
        test_framework=test_framework,
        has_ci=has_ci,
    )
