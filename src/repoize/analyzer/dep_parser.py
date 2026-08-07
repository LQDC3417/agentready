"""依赖文件解析器 — 支持多种包管理格式"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .language_profiles import LanguageProfile


class DepInfo:
    """依赖信息。"""

    def __init__(self, name: str, version_spec: str = "", dev: bool = False):
        """初始化依赖信息。"""
        self.name = name
        self.version_spec = version_spec
        self.dev = dev

    def __repr__(self) -> str:
        """返回依赖信息的字符串表示。"""
        suffix = " (dev)" if self.dev else ""
        return f"DepInfo({self.name}{suffix})"

    def to_dict(self) -> dict:
        """返回 JSON 可序列化的依赖信息。"""
        return {
            "name": self.name,
            "version_spec": self.version_spec,
            "dev": self.dev,
        }


def parse_dependencies(
    project_path: Path,
    profile: LanguageProfile | None = None,
) -> list[DepInfo]:
    """自动检测并解析项目依赖；传 profile 时按语言 manifest 解析。"""
    project_path = Path(project_path)
    parsers = _build_parsers(project_path, profile)

    all_deps: list[DepInfo] = []
    for filename, parser_fn in parsers:
        filepath = project_path / filename
        if filepath.exists():
            all_deps.extend(parser_fn(filepath))

    seen: set[str] = set()
    unique: list[DepInfo] = []
    for dep in all_deps:
        if dep.name not in seen:
            seen.add(dep.name)
            unique.append(dep)

    return unique


def _build_parsers(
    project_path: Path,
    profile: LanguageProfile | None,
) -> list[tuple[str, Callable[[Path], list[DepInfo]]]]:
    """按 profile 选择依赖解析器；无 profile 时保持默认行为。"""
    if profile is None:
        return [
            ("pyproject.toml", _parse_pyproject),
            ("requirements.txt", _parse_requirements),
            ("requirements-dev.txt", _parse_requirements_dev),
            ("package.json", _parse_package_json),
            ("go.mod", _parse_go_mod),
            ("Cargo.toml", _parse_cargo),
        ]

    if profile.name == "Python":
        return [
            ("pyproject.toml", _parse_pyproject),
            ("requirements.txt", _parse_requirements),
            ("requirements-dev.txt", _parse_requirements_dev),
        ]
    if profile.name in {"JavaScript", "TypeScript"}:
        return [("package.json", _parse_package_json)]
    if profile.name == "Go":
        return [("go.mod", _parse_go_mod)]
    if profile.name == "Rust":
        return [("Cargo.toml", _parse_cargo)]
    if profile.name == "Java":
        parsers: list[tuple[str, Callable[[Path], list[DepInfo]]]] = []
        if (project_path / "pom.xml").exists():
            parsers.append(("pom.xml", _parse_pom_xml))
        if (project_path / "build.gradle").exists():
            parsers.append(("build.gradle", _parse_gradle_build))
        return parsers
    if profile.name == "Ruby":
        return [("Gemfile", _parse_gemfile)]
    if profile.name == "PHP":
        return [("composer.json", _parse_composer_json)]
    return []


def _extract_names_from_value(value: str) -> list[str]:
    """从 TOML 值中提取包名。

    支持单行: ["fastapi>=0.100", "uvicorn"]
    和多行情况下的单个值: "fastapi>=0.100"
    """
    names: list[str] = []
    for match in re.finditer(r'"([^"]+)"', value):
        spec = match.group(1)
        name = re.split(r"[>=<!~\[]", spec)[0].strip()
        if name:
            names.append(name)
    return names


def _parse_pyproject(filepath: Path) -> list[DepInfo]:
    """解析 pyproject.toml 中的依赖。

    支持单行和多行数组格式。
    """
    deps: list[DepInfo] = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return deps

    lines = content.splitlines()
    current_section = ""
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # 检测 section 头
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip()
            i += 1
            continue

        # 检测依赖行
        is_dev = _determine_dev_status(current_section, line)
        if is_dev is None:
            i += 1
            continue

        # 解析依赖数组
        eq_pos = line.index("=")
        value_part = line[eq_pos + 1 :].strip()
        names, new_i = _parse_toml_array(lines, i, value_part)

        # 添加到结果
        for name in names:
            deps.append(DepInfo(name, dev=is_dev))

        i = new_i + 1

    return deps


def _determine_dev_status(section: str, line: str) -> bool | None:
    """确定依赖是否为开发依赖。

    Args:
        section: 当前 TOML section
        line: 当前行内容

    Returns:
        True 表示 dev 依赖，False 表示普通依赖，None 表示不是依赖行
    """
    if section == "project" and line.startswith("dependencies"):
        return False
    if section == "project.optional-dependencies" and "=" in line:
        return True
    return None


def _parse_toml_array(lines: list[str], current_idx: int, value_part: str) -> tuple[list[str], int]:
    """解析 TOML 数组，支持单行和多行格式。

    Args:
        lines: 所有行内容
        current_idx: 当前行索引
        value_part: 等号右边的值部分

    Returns:
        包名列表和最后处理的行索引
    """
    if value_part.startswith("["):
        if value_part.endswith("]"):
            # 单行数组: dependencies = ["fastapi", "uvicorn"]
            names = _extract_names_from_value(value_part)
            return names, current_idx
        else:
            # 多行数组: dependencies = [ 后面跟多行
            accumulated = value_part
            i = current_idx + 1
            while i < len(lines):
                next_line = lines[i].strip()
                accumulated += " " + next_line
                if "]" in next_line:
                    break
                i += 1
            names = _extract_names_from_value(accumulated)
            return names, i

    # 非数组格式，返回空
    return [], current_idx


def _parse_requirements(filepath: Path) -> list[DepInfo]:
    """解析 requirements.txt。"""
    deps: list[DepInfo] = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return deps

    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        line = line.split("#")[0].strip()
        name = re.split(r"[>=<!~\[]", line)[0].strip()
        if name:
            deps.append(DepInfo(name))

    return deps


def _parse_requirements_dev(filepath: Path) -> list[DepInfo]:
    """解析 dev 依赖文件。"""
    deps = _parse_requirements(filepath)
    for dep in deps:
        dep.dev = True
    return deps


def _parse_package_json(filepath: Path) -> list[DepInfo]:
    """解析 package.json。"""
    deps: list[DepInfo] = []
    try:
        import json

        data = json.loads(filepath.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, OSError, ValueError):
        return deps

    for name in data.get("dependencies", {}):
        deps.append(DepInfo(name))
    for name in data.get("devDependencies", {}):
        deps.append(DepInfo(name, dev=True))

    return deps


def _parse_go_mod(filepath: Path) -> list[DepInfo]:
    """解析 go.mod。"""
    deps: list[DepInfo] = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return deps

    in_require = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("require ("):
            in_require = True
            continue
        if stripped == ")":
            in_require = False
            continue
        if in_require or stripped.startswith("require "):
            parts = stripped.replace("require ", "").strip().split()
            if len(parts) >= 2:
                deps.append(DepInfo(parts[0], parts[1]))

    return deps


def _parse_cargo(filepath: Path) -> list[DepInfo]:
    """解析 Cargo.toml。"""
    deps: list[DepInfo] = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return deps

    in_deps = False
    in_dev_deps = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[dependencies]":
            in_deps = True
            in_dev_deps = False
            continue
        if stripped == "[dev-dependencies]":
            in_dev_deps = True
            in_deps = False
            continue
        if stripped.startswith("["):
            in_deps = False
            in_dev_deps = False
            continue

        if in_deps or in_dev_deps:
            match = re.match(r"^(\w[\w-]*)", stripped)
            if match:
                deps.append(DepInfo(match.group(1), dev=in_dev_deps))

    return deps


def _parse_pom_xml(filepath: Path) -> list[DepInfo]:
    """解析 Maven pom.xml 依赖。"""
    try:
        import xml.etree.ElementTree as ET

        root = ET.parse(filepath).getroot()
    except (OSError, ValueError, ET.ParseError):
        return []

    ns = ""
    if root.tag.startswith("{"):
        ns = root.tag.split("}")[0] + "}"

    deps: list[DepInfo] = []
    for dep in root.findall(f"{ns}dependencies/{ns}dependency"):
        group_id = dep.findtext(f"{ns}groupId", "").strip()
        artifact_id = dep.findtext(f"{ns}artifactId", "").strip()
        name = f"{group_id}:{artifact_id}" if group_id else artifact_id
        if name:
            deps.append(DepInfo(name))
    return deps


def _parse_gradle_build(filepath: Path) -> list[DepInfo]:
    """保守解析 Gradle 常见依赖声明。"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    deps: list[DepInfo] = []
    pattern = re.compile(r"(?:implementation|api|compileOnly|runtimeOnly)\s*\(?\s*['\"]([^'\"]+)['\"]")
    for line in content.splitlines():
        match = pattern.search(line)
        if not match:
            continue
        raw = match.group(1)
        parts = raw.split(":")
        name = ":".join(parts[:2])
        deps.append(DepInfo(name))
    return deps


def _parse_gemfile(filepath: Path) -> list[DepInfo]:
    """解析 Gemfile 中的 gem 声明。"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    deps: list[DepInfo] = []
    for line in content.splitlines():
        stripped = line.strip()
        match = re.match(r'^gem\s+["\']([^"\']+)["\']', stripped)
        if match:
            deps.append(DepInfo(match.group(1)))
    return deps


def _parse_composer_json(filepath: Path) -> list[DepInfo]:
    """解析 composer.json 依赖。"""
    try:
        import json

        data = json.loads(filepath.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, OSError, ValueError):
        return []

    deps: list[DepInfo] = []
    for name in data.get("require", {}):
        deps.append(DepInfo(name))
    for name in data.get("require-dev", {}):
        deps.append(DepInfo(name, dev=True))
    return deps
