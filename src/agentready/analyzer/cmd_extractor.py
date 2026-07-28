"""构建/测试/lint 命令提取器"""

import re
from pathlib import Path


class CommandSet:
    """项目命令集合。"""

    def __init__(self):
        self.build: list[str] = []
        self.test: list[str] = []
        self.lint: list[str] = []
        self.format: list[str] = []
        self.run: list[str] = []

    def to_dict(self) -> dict:
        return {
            "build": self.build,
            "test": self.test,
            "lint": self.lint,
            "format": self.format,
            "run": self.run,
        }


def extract_commands(project_path: Path) -> CommandSet:
    """从项目配置文件中提取构建/测试/lint 命令。"""
    project_path = Path(project_path)
    cmds = CommandSet()

    _extract_from_pyproject(project_path, cmds)
    _extract_from_package_json(project_path, cmds)
    _extract_from_makefile(project_path, cmds)
    _extract_from_go(project_path, cmds)
    _extract_from_cargo(project_path, cmds)

    return cmds


def _extract_from_pyproject(project_path: Path, cmds: CommandSet):
    """从 pyproject.toml 提取命令。"""
    filepath = project_path / "pyproject.toml"
    if not filepath.exists():
        return

    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return

    # 检测测试框架
    if "pytest" in content or "testpaths" in content:
        cmds.test.append("pytest")

    # 检测 lint 工具
    if "[tool.ruff" in content:
        cmds.lint.append("ruff check .")
        cmds.format.append("ruff format .")
    if "[tool.mypy" in content:
        cmds.lint.append("mypy .")
    if "[tool.flake8" in content:
        cmds.lint.append("flake8 .")
    if "[tool.black" in content:
        cmds.format.append("black .")
    if "[tool.isort" in content:
        cmds.format.append("isort .")

    # 提取 scripts
    in_scripts = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[project.scripts]" or stripped == "[tool.poetry.scripts]":
            in_scripts = True
            continue
        if stripped.startswith("[") and in_scripts:
            in_scripts = False
            continue
        if in_scripts and "=" in stripped:
            name = stripped.split("=")[0].strip()
            if name:
                cmds.run.append(f"python -m {name}")


def _extract_from_package_json(project_path: Path, cmds: CommandSet):
    """从 package.json 提取 scripts。"""
    filepath = project_path / "package.json"
    if not filepath.exists():
        return

    try:
        import json

        data = json.loads(filepath.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, OSError, ValueError):
        return

    scripts = data.get("scripts", {})
    script_map = {
        "build": cmds.build,
        "test": cmds.test,
        "lint": cmds.lint,
        "format": cmds.format,
        "start": cmds.run,
        "dev": cmds.run,
    }
    for script_name, target_list in script_map.items():
        if script_name in scripts:
            target_list.append(f"npm run {script_name}")


def _extract_from_makefile(project_path: Path, cmds: CommandSet):
    """从 Makefile 提取常见目标。"""
    for makefile_name in ["Makefile", "makefile", "GNUmakefile"]:
        filepath = project_path / makefile_name
        if filepath.exists():
            break
    else:
        return

    try:
        content = filepath.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return

    # 提取顶层目标
    targets = re.findall(r"^([a-zA-Z][\w-]*)\s*:", content, re.MULTILINE)
    target_map = {
        "build": cmds.build,
        "test": cmds.test,
        "check": cmds.lint,
        "lint": cmds.lint,
        "fmt": cmds.format,
        "format": cmds.format,
        "run": cmds.run,
        "start": cmds.run,
        "serve": cmds.run,
        "dev": cmds.run,
    }
    for target in targets:
        target_lower = target.lower()
        if target_lower in target_map:
            cmd = f"make {target}"
            if cmd not in target_map[target_lower]:
                target_map[target_lower].append(cmd)


def _extract_from_go(project_path: Path, cmds: CommandSet):
    """Go 项目命令提取。"""
    if (project_path / "go.mod").exists():
        cmds.build.append("go build ./...")
        cmds.test.append("go test ./...")
        cmds.lint.append("golangci-lint run")


def _extract_from_cargo(project_path: Path, cmds: CommandSet):
    """Rust 项目命令提取。"""
    if (project_path / "Cargo.toml").exists():
        cmds.build.append("cargo build")
        cmds.test.append("cargo test")
        cmds.lint.append("cargo clippy")
        cmds.format.append("cargo fmt")
        cmds.run.append("cargo run")
