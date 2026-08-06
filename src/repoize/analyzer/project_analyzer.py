"""主分析器 — 协调各子模块，输出完整项目分析结果"""

from dataclasses import dataclass, field
from pathlib import Path

from .cmd_extractor import CommandSet, extract_commands
from .config_scanner import ConfigStatus, scan_existing_configs
from .dep_parser import DepInfo, parse_dependencies
from .env_scanner import EnvInfo, scan_environment
from .lang_detector import IGNORE_DIRS, detect_languages, get_primary_language
from .language_profiles import LanguageProfile, detect_frameworks, get_language_profile
from .quality_analyzer import CodeQualityMetrics, analyze_code_quality

_TREE_MAX_DEPTH = 2

# 测试框架检测映射
_TEST_FRAMEWORK_PATTERNS: list[tuple[str, str]] = [
    ("pytest", "pytest"),
    ("jest", "jest"),
    ("go test", "go test"),
    ("cargo test", "cargo test"),
]


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
    env_info: EnvInfo = field(default_factory=EnvInfo)
    has_tests: bool = False
    test_framework: str | None = None
    has_ci: bool = False
    profile: LanguageProfile | None = None
    frameworks: list[str] = field(default_factory=list)
    directory_tree: str = ""
    quality_metrics: CodeQualityMetrics = field(default_factory=CodeQualityMetrics)

    @property
    def agent_ready_score(self) -> int:
        """Agent 就绪度评分（0-100）。"""
        score = 0
        existing_types = {c.config_type for c in self.existing_configs if c.exists}
        if "agents_md" in existing_types:
            score += 25
        if "claude_md" in existing_types:
            score += 15
        if "cursorrules" in existing_types:
            score += 15
        if "copilot" in existing_types:
            score += 15
        if "mcp_claude" in existing_types or "mcp_desktop" in existing_types:
            score += 20
        if "skill" in existing_types or "skill_claude" in existing_types:
            score += 10
        return min(score, 100)

    @property
    def agent_ready_label(self) -> str:
        """Agent 就绪度标签。"""
        s = self.agent_ready_score
        if s >= 80:
            return "完备"
        if s >= 40:
            return "部分就绪"
        return "未配置"

    @property
    def code_quality_score(self) -> int:
        """代码质量评分（0-100）。"""
        score = 50  # 基础分

        # 有代码质量工具加分
        if self.quality_metrics.quality_tools_found:
            score += 20

        # 有代码质量配置加分
        if self.quality_metrics.quality_config_found:
            score += 15

        # 有测试加分
        if self.has_tests:
            score += 10

        # 有CI加分
        if self.has_ci:
            score += 5

        # 代码行数合理性（避免过大的文件）
        if self.quality_metrics.total_files > 0:
            avg_lines = self.quality_metrics.total_lines / self.quality_metrics.total_files
            if 100 <= avg_lines <= 500:
                score += 10  # 合理的文件大小
            elif avg_lines > 1000:
                score -= 10  # 文件过大

        return min(max(score, 0), 100)

    @property
    def code_quality_label(self) -> str:
        """代码质量标签。"""
        s = self.code_quality_score
        if s >= 80:
            return "优秀"
        if s >= 60:
            return "良好"
        if s >= 40:
            return "一般"
        return "需要改进"

    def to_dict(self) -> dict:
        """返回 JSON 可序列化的项目分析结果。"""
        return {
            "schema_version": 1,
            "project_name": self.project_name,
            "project_path": str(self.project_path),
            "primary_language": self.primary_language,
            "languages": self.languages,
            "profile": self.profile.name if self.profile else None,
            "frameworks": self.frameworks,
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "commands": self.commands.to_dict(),
            "existing_configs": [cfg.to_dict() for cfg in self.existing_configs],
            "env_info": self.env_info.to_dict(),
            "has_tests": self.has_tests,
            "test_framework": self.test_framework,
            "has_ci": self.has_ci,
            "agent_ready_score": self.agent_ready_score,
            "agent_ready_label": self.agent_ready_label,
            "code_quality_score": self.code_quality_score,
            "code_quality_label": self.code_quality_label,
            "quality_metrics": self.quality_metrics.to_dict(),
        }


def _detect_test_setup(project_path: Path, commands: CommandSet) -> tuple[bool, str | None]:
    """检测项目的测试配置。

    Args:
        project_path: 项目根目录
        commands: 提取的命令集

    Returns:
        (has_tests, test_framework) 元组
    """
    # 1. 从命令中检测测试框架
    if commands.test:
        test_cmd = commands.test[0].lower()
        for pattern, framework in _TEST_FRAMEWORK_PATTERNS:
            if pattern in test_cmd:
                return True, framework
        return True, None

    # 2. 检测测试目录
    if (project_path / "tests").is_dir() or (project_path / "test").is_dir():
        return True, None

    return False, None


def _detect_ci_config(project_path: Path) -> bool:
    """检测项目是否配置了 CI/CD。

    Args:
        project_path: 项目根目录

    Returns:
        是否有 CI 配置
    """
    ci_indicators = [
        (".github", "workflows"),  # GitHub Actions
        ".gitlab-ci.yml",  # GitLab CI
        "Jenkinsfile",  # Jenkins
        ".circleci",  # CircleCI
    ]

    for indicator in ci_indicators:
        if isinstance(indicator, tuple):
            # 目录结构检查
            dir_name, sub_dir = indicator
            if (project_path / dir_name / sub_dir).is_dir():
                return True
        else:
            # 文件检查
            if (project_path / indicator).exists():
                return True

    return False


def analyze_project(project_path: Path, scan_env: bool = True) -> ProjectAnalysis:
    """执行完整的项目分析。

    Args:
        project_path: 项目根目录
        scan_env: 是否扫描系统环境变量（默认 True）

    Returns:
        项目分析结果
    """
    project_path = Path(project_path).resolve()

    # 1. 基础分析
    languages = detect_languages(project_path)
    primary = get_primary_language(project_path)
    profile = get_language_profile(primary)

    # 2. 依赖和命令分析
    deps = parse_dependencies(project_path, profile=profile)
    cmds = extract_commands(project_path, profile=profile)

    # 3. 配置和框架检测
    configs = scan_existing_configs(project_path)
    frameworks = detect_frameworks(profile, deps)

    # 4. 环境扫描
    env = scan_environment() if scan_env else EnvInfo()

    # 5. 测试和 CI 检测
    has_tests, test_framework = _detect_test_setup(project_path, cmds)
    has_ci = _detect_ci_config(project_path)

    # 6. 生成目录树
    directory_tree = _build_directory_tree(project_path)

    # 7. 分析代码质量
    dep_names = [dep.name for dep in deps]
    quality_metrics = analyze_code_quality(project_path, profile, dep_names)

    return ProjectAnalysis(
        project_path=project_path,
        project_name=project_path.name,
        languages=languages,
        primary_language=primary,
        dependencies=deps,
        commands=cmds,
        existing_configs=configs,
        env_info=env,
        has_tests=has_tests,
        test_framework=test_framework,
        has_ci=has_ci,
        profile=profile,
        frameworks=frameworks,
        directory_tree=directory_tree,
        quality_metrics=quality_metrics,
    )


def _build_directory_tree(root: Path, max_depth: int = _TREE_MAX_DEPTH) -> str:
    """生成项目目录树文本（类似 tree -L 2），跳过忽略目录。

    Args:
        root: 项目根目录
        max_depth: 最大遍历深度

    Returns:
        目录树文本
    """
    hidden_exceptions = {".github", ".gitlab-ci.yml"}
    lines: list[str] = [f"{root.name}/"]
    _walk_tree(root, "", max_depth, 0, hidden_exceptions, lines)
    return "\n".join(lines)


def _walk_tree(
    current: Path,
    prefix: str,
    max_depth: int,
    depth: int,
    hidden_exceptions: set[str],
    lines: list[str],
) -> None:
    """递归遍历目录，生成树形文本。

    Args:
        current: 当前遍历的目录
        prefix: 当前行的前缀（用于缩进和连接线）
        max_depth: 最大遍历深度
        depth: 当前深度
        hidden_exceptions: 需要显示的隐藏目录/文件集合
        lines: 输出行列表
    """
    if depth >= max_depth:
        return
    try:
        entries = sorted(current.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower()))
    except PermissionError:
        return

    visible = []
    for entry in entries:
        name = entry.name
        if name.startswith(".") and name not in hidden_exceptions:
            continue
        if entry.is_dir() and name in IGNORE_DIRS:
            continue
        visible.append(entry)

    for i, entry in enumerate(visible):
        is_last = i == len(visible) - 1
        connector = "└── " if is_last else "├── "
        child_prefix = prefix + ("    " if is_last else "│   ")
        suffix = "/" if entry.is_dir() else ""
        lines.append(f"{prefix}{connector}{entry.name}{suffix}")
        if entry.is_dir():
            _walk_tree(entry, child_prefix, max_depth, depth + 1, hidden_exceptions, lines)
