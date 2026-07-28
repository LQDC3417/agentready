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

    # 去重（保留第一个遇到的）
    seen: set[str] = set()
    unique: list[DepInfo] = []
    for dep in all_deps:
        if dep.name not in seen:
            seen.add(dep.name)
            unique.append(dep)

    return unique


def _parse_pyproject(filepath: Path) -> list[DepInfo]:
    """解析 pyproject.toml 中的依赖。"""
    deps: list[DepInfo] = []
    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return deps

    # 简易解析 dependencies 数组
    in_deps = False
    in_dev_deps = False
    for line in content.splitlines():
        stripped = line.strip()

        if stripped == "dependencies = [":
            in_deps = True
            in_dev_deps = False
            continue
        if "optional-dependencies" in stripped:
            in_dev_deps = True
            in_deps = False
            continue
        if stripped == "]":
            in_deps = False
            in_dev_deps = False
            continue

        if in_deps or in_dev_deps:
            # 提取引号中的包名
            match = re.search(r'"([^"]+)"', stripped)
            if match:
                spec = match.group(1)
                name = re.split(r"[>=<!~\[]", spec)[0].strip()
                if name:
                    deps.append(DepInfo(name, dev=in_dev_deps))

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
        # 去除行内注释
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
