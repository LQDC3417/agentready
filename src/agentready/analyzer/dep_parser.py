"""依赖文件解析器 — 支持多种包管理格式"""

from pathlib import Path
import re


class DepInfo:
    """依赖信息。"""

    def __init__(self, name: str, version_spec: str = "", dev: bool = False):
        self.name = name
        self.version_spec = version_spec
        self.dev = dev

    def __repr__(self) -> str:
        suffix = " (dev)" if self.dev else ""
        return f"DepInfo({self.name}{suffix})"


def parse_dependencies(project_path: Path) -> list[DepInfo]:
    """自动检测并解析项目依赖文件。"""
    project_path = Path(project_path)
    parsers = [
        ("pyproject.toml", _parse_pyproject),
        ("requirements.txt", _parse_requirements),
        ("requirements-dev.txt", _parse_requirements_dev),
        ("package.json", _parse_package_json),
        ("go.mod", _parse_go_mod),
        ("Cargo.toml", _parse_cargo),
    ]

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

        # 只在 [project] 和 [project.optional-dependencies] 下解析依赖
        if current_section == "project" and line.startswith("dependencies"):
            is_dev = False
        elif current_section == "project.optional-dependencies" and "=" in line:
            is_dev = True
        else:
            i += 1
            continue

        # 提取 = 右边的值
        eq_pos = line.index("=")
        value_part = line[eq_pos + 1:].strip()

        if value_part.startswith("["):
            if value_part.endswith("]"):
                # 单行数组: dependencies = ["fastapi", "uvicorn"]
                names = _extract_names_from_value(value_part)
                for name in names:
                    deps.append(DepInfo(name, dev=is_dev))
            else:
                # 多行数组: dependencies = [ 后面跟多行
                # 把 [ 后面的部分也一起处理
                accumulated = value_part
                i += 1
                while i < len(lines):
                    next_line = lines[i].strip()
                    accumulated += " " + next_line
                    if "]" in next_line:
                        break
                    i += 1
                names = _extract_names_from_value(accumulated)
                for name in names:
                    deps.append(DepInfo(name, dev=is_dev))

        i += 1

    return deps


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
