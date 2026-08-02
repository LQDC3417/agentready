# Multi-Language Profiles Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 repoize 通过 language profile 支持 JS/TS、Go、Rust、Java、Ruby、PHP 的基础分析和配置生成。

**Architecture:** 新增 language profile 注册表，Analyzer 输出 profile 和 frameworks，所有生成器把这两项传给 Jinja2 模板，模板据此渲染语言正确的安装和命令。

**Tech Stack:** Python 3.10+、click、rich、jinja2、pytest、ruff。

---

## Commit Policy

本仓库 AGENTS.md 约定不自动 commit。执行时每个任务末尾的 commit 步骤必须先向用户确认，得到确认后再执行。

## File Structure

新增文件：

- `src/repoize/analyzer/language_profiles.py`
- `tests/test_language_profiles.py`
- `tests/test_cmd_extractor.py`
- `tests/fixtures/languages/javascript/package.json`
- `tests/fixtures/languages/typescript/package.json`
- `tests/fixtures/languages/typescript/tsconfig.json`
- `tests/fixtures/languages/go/go.mod`
- `tests/fixtures/languages/rust/Cargo.toml`
- `tests/fixtures/languages/java/pom.xml`
- `tests/fixtures/languages/ruby/Gemfile`
- `tests/fixtures/languages/php/composer.json`

修改文件：

- `src/repoize/analyzer/dep_parser.py`
- `src/repoize/analyzer/cmd_extractor.py`
- `src/repoize/analyzer/project_analyzer.py`
- `src/repoize/generator/agents_md.py`
- `src/repoize/generator/claude_md.py`
- `src/repoize/generator/cursorrules.py`
- `src/repoize/generator/copilot.py`
- `src/repoize/generator/mcp_config.py`
- `src/repoize/generator/skill_md.py`
- `src/repoize/reporter/health_report.py`
- `src/repoize/templates/agents_md.j2`
- `src/repoize/templates/claude_md.j2`
- `src/repoize/templates/cursorrules.j2`
- `src/repoize/templates/copilot.j2`
- `src/repoize/templates/mcp_config.j2`
- `src/repoize/templates/skill_md.j2`
- `tests/test_dep_parser.py`
- `tests/test_generators.py`
- `tests/test_analyzer.py`

---

### Task 1: Language Profile 注册表

**Files:**
- Create: `src/repoize/analyzer/language_profiles.py`
- Test: `tests/test_language_profiles.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_language_profiles.py`:

```python
from repoize.analyzer.dep_parser import DepInfo
from repoize.analyzer.language_profiles import detect_frameworks, get_language_profile


def test_get_language_profile_go():
    profile = get_language_profile("Go")
    assert profile is not None
    assert profile.manifest_files == ("go.mod",)
    assert "go test ./..." in profile.commands["test"]


def test_get_language_profile_unknown():
    assert get_language_profile("Unknown") is None
    assert get_language_profile(None) is None


def test_detect_frameworks_go():
    profile = get_language_profile("Go")
    deps = [DepInfo("gin"), DepInfo("gorm")]
    assert detect_frameworks(profile, deps) == ["gin"]


def test_detect_frameworks_empty():
    profile = get_language_profile("Rust")
    deps = [DepInfo("serde")]
    assert detect_frameworks(profile, deps) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_language_profiles.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'repoize.analyzer.language_profiles'`

- [ ] **Step 3: Create the profile module**

Create `src/repoize/analyzer/language_profiles.py`:

```python
"""语言画像注册表：为多语言分析、命令提取和模板渲染提供默认知识。"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class LanguageProfile:
    """一种语言的 manifest、默认命令和框架关键词。"""

    name: str
    manifest_files: tuple[str, ...] = ()
    setup_commands: tuple[str, ...] = ()
    commands: dict[str, tuple[str, ...]] = field(default_factory=dict)
    framework_keywords: tuple[str, ...] = ()


PROFILES: tuple[LanguageProfile, ...] = (
    LanguageProfile(
        name="Python",
        manifest_files=("pyproject.toml", "requirements.txt", "requirements-dev.txt"),
        setup_commands=('pip install -e ".[dev]"',),
        commands={
            "build": ("python -m build",),
            "test": ("pytest",),
            "lint": ("ruff check .",),
            "format": ("ruff format .",),
        },
        framework_keywords=("fastapi", "django", "flask", "sqlalchemy"),
    ),
    LanguageProfile(
        name="JavaScript",
        manifest_files=("package.json",),
        setup_commands=("npm install",),
        commands={
            "test": ("npm test",),
            "lint": ("npm run lint",),
            "format": ("npm run format",),
        },
        framework_keywords=("next", "react", "express", "vue", "svelte", "astro"),
    ),
    LanguageProfile(
        name="TypeScript",
        manifest_files=("package.json",),
        setup_commands=("npm install",),
        commands={
            "test": ("npm test",),
            "lint": ("npm run lint",),
            "format": ("npm run format",),
        },
        framework_keywords=("next", "react", "express", "vue", "svelte", "astro"),
    ),
    LanguageProfile(
        name="Go",
        manifest_files=("go.mod",),
        setup_commands=("go mod download",),
        commands={
            "build": ("go build ./...",),
            "test": ("go test ./...",),
            "lint": ("golangci-lint run",),
            "format": ("gofmt -w .",),
        },
        framework_keywords=("gin", "echo", "fiber"),
    ),
    LanguageProfile(
        name="Rust",
        manifest_files=("Cargo.toml",),
        setup_commands=("cargo build",),
        commands={
            "build": ("cargo build",),
            "test": ("cargo test",),
            "lint": ("cargo clippy -- -D warnings",),
            "format": ("cargo fmt --check",),
        },
        framework_keywords=("axum", "actix-web", "rocket"),
    ),
    LanguageProfile(
        name="Java",
        manifest_files=("pom.xml", "build.gradle"),
        setup_commands=("mvn -q dependency:resolve",),
        commands={
            "build": ("mvn verify",),
            "test": ("mvn test",),
            "lint": ("mvn checkstyle:check",),
        },
        framework_keywords=("spring-boot", "spring-web", "quarkus"),
    ),
    LanguageProfile(
        name="Ruby",
        manifest_files=("Gemfile",),
        setup_commands=("bundle install",),
        commands={
            "build": ("bundle exec rake build",),
            "test": ("bundle exec rake test",),
            "lint": ("bundle exec rubocop",),
        },
        framework_keywords=("rails", "sinatra"),
    ),
    LanguageProfile(
        name="PHP",
        manifest_files=("composer.json",),
        setup_commands=("composer install",),
        commands={
            "test": ("vendor/bin/phpunit",),
            "lint": ("vendor/bin/php-cs-fixer check",),
            "format": ("vendor/bin/php-cs-fixer fix",),
        },
        framework_keywords=("laravel", "symfony"),
    ),
)


def get_language_profile(language: str | None) -> LanguageProfile | None:
    """返回语言对应的 profile，未知语言返回 None。"""
    if language is None:
        return None
    for profile in PROFILES:
        if profile.name == language:
            return profile
    return None


def detect_frameworks(profile: LanguageProfile | None, dependencies: list[DepInfo]) -> list[str]:
    """根据依赖名识别 profile 中的框架关键词。"""
    if profile is None:
        return []
    names = [dep.name.lower() for dep in dependencies]
    found: list[str] = []
    for keyword in profile.framework_keywords:
        if any(keyword in name for name in names):
            found.append(keyword)
    return found
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_language_profiles.py -v`
Expected: PASS

- [ ] **Step 5: Commit after user confirmation**

```bash
git add src/repoize/analyzer/language_profiles.py tests/test_language_profiles.py
git commit -m "feat: add language profile registry"
```

---

### Task 2: 扩展依赖解析器

**Files:**
- Modify: `src/repoize/analyzer/dep_parser.py`
- Test: `tests/test_dep_parser.py`

- [ ] **Step 1: Add failing parser tests**

Append to `tests/test_dep_parser.py`:

```python
from repoize.analyzer.language_profiles import get_language_profile


def test_parse_pom_xml(tmp_path):
    content = """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
      <artifactId>junit</artifactId>
      <version>4.13.2</version>
      <scope>test</scope>
    </dependency>
  </dependencies>
</project>
"""
    (tmp_path / "pom.xml").write_text(content, encoding="utf-8")
    deps = parse_dependencies(tmp_path, profile=get_language_profile("Java"))
    names = [d.name for d in deps]
    assert "org.springframework.boot:spring-boot-starter-web" in names
    assert "junit" in names


def test_parse_gradle_build(tmp_path):
    content = """dependencies {
    implementation 'com.google.guava:guava:33.0.0-jre'
    api "org.slf4j:slf4j-api:2.0.13"
    testImplementation 'junit:junit:4.13.2'
}
"""
    (tmp_path / "build.gradle").write_text(content, encoding="utf-8")
    deps = parse_dependencies(tmp_path, profile=get_language_profile("Java"))
    names = [d.name for d in deps]
    assert "com.google.guava:guava" in names
    assert "org.slf4j:slf4j-api" in names


def test_parse_gemfile(tmp_path):
    content = """source "https://rubygems.org"
gem "rails", "~> 7.0"
gem "puma"
"""
    (tmp_path / "Gemfile").write_text(content, encoding="utf-8")
    deps = parse_dependencies(tmp_path, profile=get_language_profile("Ruby"))
    names = [d.name for d in deps]
    assert "rails" in names
    assert "puma" in names


def test_parse_composer_json(tmp_path):
    content = """{
  "require": {
    "laravel/framework": "^11.0"
  },
  "require-dev": {
    "phpunit/phpunit": "^11.0"
  }
}
"""
    (tmp_path / "composer.json").write_text(content, encoding="utf-8")
    deps = parse_dependencies(tmp_path, profile=get_language_profile("PHP"))
    phpunit = next(d for d in deps if d.name == "phpunit/phpunit")
    assert phpunit.dev is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_dep_parser.py -v`
Expected: FAIL on `_parse_pom_xml` and `_parse_gradle_build` undefined

- [ ] **Step 3: Add profile-aware parsing**

Modify `parse_dependencies` in `src/repoize/analyzer/dep_parser.py`:

```python
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
```

Add helper functions:

```python
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
```

Add the new parsers:

```python
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
    pattern = re.compile(
        r"(?:implementation|api|compileOnly|runtimeOnly)\s*\(?\s*['\"]([^'\"]+)['\"]"
    )
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
```

Update the import line in `src/repoize/analyzer/dep_parser.py`:

```python
from typing import Callable

from .language_profiles import LanguageProfile
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_dep_parser.py -v`
Expected: PASS

- [ ] **Step 5: Commit after user confirmation**

```bash
git add src/repoize/analyzer/dep_parser.py tests/test_dep_parser.py
git commit -m "feat: parse Java Ruby PHP manifests"
```

---

### Task 3: 命令提取器支持 profile

**Files:**
- Modify: `src/repoize/analyzer/cmd_extractor.py`
- Test: `tests/test_cmd_extractor.py`

- [ ] **Step 1: Add failing command tests**

Create `tests/test_cmd_extractor.py`:

```python
from repoize.analyzer.cmd_extractor import extract_commands
from repoize.analyzer.language_profiles import get_language_profile


def test_go_profile_fills_default_commands(tmp_path):
    (tmp_path / "go.mod").write_text("module example.com/foo\n\ngo 1.22\n", encoding="utf-8")
    cmds = extract_commands(tmp_path, profile=get_language_profile("Go"))
    assert "go build ./..." in cmds.build
    assert "go test ./..." in cmds.test
    assert "gofmt -w ." in cmds.format


def test_package_scripts_take_priority(tmp_path):
    content = """{
  "scripts": {
    "build": "vite build",
    "test": "vitest run",
    "lint": "eslint ."
  }
}
"""
    (tmp_path / "package.json").write_text(content, encoding="utf-8")
    cmds = extract_commands(tmp_path, profile=get_language_profile("JavaScript"))
    assert "npm run build" in cmds.build
    assert "npm run lint" in cmds.lint


def test_java_maven_commands(tmp_path):
    (tmp_path / "pom.xml").write_text("<project></project>", encoding="utf-8")
    cmds = extract_commands(tmp_path, profile=get_language_profile("Java"))
    assert "mvn verify" in cmds.build
    assert "mvn test" in cmds.test


def test_php_composer_scripts(tmp_path):
    content = """{
  "scripts": {
    "test": "phpunit",
    "lint": "php-cs-fixer check"
  }
}
"""
    (tmp_path / "composer.json").write_text(content, encoding="utf-8")
    cmds = extract_commands(tmp_path, profile=get_language_profile("PHP"))
    assert "composer run test" in cmds.test
    assert "composer run lint" in cmds.lint
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_cmd_extractor.py -v`
Expected: FAIL because `extract_commands` has no `profile` parameter

- [ ] **Step 3: Implement profile defaults and language extraction**

Modify `extract_commands` in `src/repoize/analyzer/cmd_extractor.py`:

```python
def extract_commands(
    project_path: Path,
    profile: LanguageProfile | None = None,
) -> CommandSet:
    """从项目配置文件中提取命令；profile 提供默认命令兜底。"""
    project_path = Path(project_path)
    cmds = CommandSet()

    _extract_from_pyproject(project_path, cmds)
    _extract_from_package_json(project_path, cmds)
    _extract_from_makefile(project_path, cmds)
    _extract_from_go(project_path, cmds)
    _extract_from_cargo(project_path, cmds)
    _extract_from_java(project_path, cmds)
    _extract_from_ruby(project_path, cmds)
    _extract_from_php(project_path, cmds)
    _apply_profile_defaults(cmds, profile)

    return cmds
```

Add imports:

```python
from .language_profiles import LanguageProfile
```

Add helper functions:

```python
def _apply_profile_defaults(cmds: CommandSet, profile: LanguageProfile | None):
    """只在对应分类为空时填充 profile 默认命令。"""
    if profile is None:
        return
    target_map = {
        "build": cmds.build,
        "test": cmds.test,
        "lint": cmds.lint,
        "format": cmds.format,
        "run": cmds.run,
    }
    for category, commands in profile.commands.items():
        target = target_map.get(category)
        if target is not None and not target:
            target.extend(commands)


def _extract_from_java(project_path: Path, cmds: CommandSet):
    """Java Maven/Gradle 命令提取。"""
    if (project_path / "pom.xml").exists():
        cmds.build.append("mvn verify")
        cmds.test.append("mvn test")
        cmds.lint.append("mvn checkstyle:check")
    elif (project_path / "build.gradle").exists():
        cmds.build.append("gradle build")
        cmds.test.append("gradle test")
        cmds.lint.append("gradle check")


def _extract_from_ruby(project_path: Path, cmds: CommandSet):
    """Ruby Rake/RuboCop 命令提取。"""
    if (project_path / "Gemfile").exists():
        cmds.build.append("bundle exec rake build")
        cmds.test.append("bundle exec rake test")
        cmds.lint.append("bundle exec rubocop")


def _extract_from_php(project_path: Path, cmds: CommandSet):
    """PHP composer scripts 提取，无 scripts 时给出 phpunit 默认。"""
    filepath = project_path / "composer.json"
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
    }
    for script_name, target_list in script_map.items():
        if script_name in scripts:
            target_list.append(f"composer run {script_name}")
    if not cmds.test:
        cmds.test.append("vendor/bin/phpunit")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_cmd_extractor.py -v`
Expected: PASS

- [ ] **Step 5: Commit after user confirmation**

```bash
git add src/repoize/analyzer/cmd_extractor.py tests/test_cmd_extractor.py
git commit -m "feat: add profile-aware command extraction"
```

---

### Task 4: Analyzer 输出 profile 和 frameworks

**Files:**
- Modify: `src/repoize/analyzer/project_analyzer.py`
- Test: `tests/test_analyzer.py`

- [ ] **Step 1: Add failing analyzer tests**

Append to `tests/test_analyzer.py`:

```python
def test_analyze_go_profile(tmp_path):
    """测试 Go 项目匹配 profile 并提取命令。"""
    (tmp_path / "go.mod").write_text("module example.com/foo\n\ngo 1.22\n", encoding="utf-8")
    (tmp_path / "main.go").write_text("package main\n", encoding="utf-8")
    analysis = analyze_project(tmp_path, scan_env=False)
    assert analysis.primary_language == "Go"
    assert analysis.profile is not None
    assert "go test ./..." in analysis.commands.test


def test_analyze_frameworks(tmp_path):
    """测试框架识别写入分析结果。"""
    content = """{
  "dependencies": {
    "express": "^4.19.0"
  }
}
"""
    (tmp_path / "package.json").write_text(content, encoding="utf-8")
    (tmp_path / "index.js").write_text("console.log('hi')", encoding="utf-8")
    analysis = analyze_project(tmp_path, scan_env=False)
    assert analysis.frameworks == ["express"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_analyzer.py -v`
Expected: FAIL with `AttributeError: 'ProjectAnalysis' object has no attribute 'profile'`

- [ ] **Step 3: Extend ProjectAnalysis and analyze_project**

Modify imports in `src/repoize/analyzer/project_analyzer.py`:

```python
from .language_profiles import LanguageProfile, detect_frameworks, get_language_profile
```

Add fields to `ProjectAnalysis`:

```python
    profile: LanguageProfile | None = None
    frameworks: list[str] = field(default_factory=list)
```

Modify `analyze_project`:

```python
    languages = detect_languages(project_path)
    primary = get_primary_language(project_path)
    profile = get_language_profile(primary)
    deps = parse_dependencies(project_path, profile=profile)
    cmds = extract_commands(project_path, profile=profile)
    configs = scan_existing_configs(project_path)
    frameworks = detect_frameworks(profile, deps)
```

Add to the returned `ProjectAnalysis`:

```python
        profile=profile,
        frameworks=frameworks,
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_analyzer.py -v`
Expected: PASS

- [ ] **Step 5: Commit after user confirmation**

```bash
git add src/repoize/analyzer/project_analyzer.py tests/test_analyzer.py
git commit -m "feat: expose language profile and frameworks from analyzer"
```

---

### Task 5: 添加语言 fixture 项目

**Files:**
- Create: `tests/fixtures/languages/javascript/package.json`
- Create: `tests/fixtures/languages/typescript/package.json`
- Create: `tests/fixtures/languages/typescript/tsconfig.json`
- Create: `tests/fixtures/languages/go/go.mod`
- Create: `tests/fixtures/languages/rust/Cargo.toml`
- Create: `tests/fixtures/languages/java/pom.xml`
- Create: `tests/fixtures/languages/ruby/Gemfile`
- Create: `tests/fixtures/languages/php/composer.json`

- [ ] **Step 1: Create fixture files**

`tests/fixtures/languages/javascript/package.json`:

```json
{
  "name": "javascript-fixture",
  "scripts": {
    "build": "vite build",
    "test": "vitest run",
    "lint": "eslint .",
    "format": "prettier --write ."
  },
  "dependencies": {
    "react": "^18.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  }
}
```

`tests/fixtures/languages/typescript/package.json`:

```json
{
  "name": "typescript-fixture",
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "test": "vitest run",
    "lint": "eslint .",
    "format": "prettier --write ."
  },
  "dependencies": {
    "next": "^14.0.0"
  },
  "devDependencies": {
    "typescript": "^5.0.0"
  }
}
```

`tests/fixtures/languages/typescript/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext"
  }
}
```

`tests/fixtures/languages/go/go.mod`:

```
module example.com/go-fixture

go 1.22
```

`tests/fixtures/languages/rust/Cargo.toml`:

```toml
[package]
name = "rust-fixture"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = "1"
```

`tests/fixtures/languages/java/pom.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>example</groupId>
  <artifactId>java-fixture</artifactId>
  <version>0.1.0</version>
  <dependencies>
    <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
      <version>3.2.0</version>
    </dependency>
  </dependencies>
</project>
```

`tests/fixtures/languages/ruby/Gemfile`:

```
source "https://rubygems.org"

gem "rails", "~> 7.1"
gem "puma"
```

`tests/fixtures/languages/php/composer.json`:

```json
{
  "name": "example/php-fixture",
  "require": {
    "laravel/framework": "^11.0"
  },
  "require-dev": {
    "phpunit/phpunit": "^11.0"
  },
  "scripts": {
    "test": "phpunit",
    "lint": "php-cs-fixer check"
  }
}
```

- [ ] **Step 2: Verify fixtures are discoverable**

Run: `python -m pytest tests/test_lang_detector.py -v`
Expected: PASS

- [ ] **Step 3: Commit after user confirmation**

```bash
git add tests/fixtures
git commit -m "test: add multi-language fixtures"
```

---

### Task 6: 生成器传入 profile 和 frameworks

**Files:**
- Modify: `src/repoize/generator/agents_md.py`
- Modify: `src/repoize/generator/claude_md.py`
- Modify: `src/repoize/generator/cursorrules.py`
- Modify: `src/repoize/generator/copilot.py`
- Modify: `src/repoize/generator/mcp_config.py`
- Modify: `src/repoize/generator/skill_md.py`

- [ ] **Step 1: Add profile/frameworks to every render call**

`src/repoize/generator/agents_md.py`:

```python
        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            languages=self.analysis.languages,
            dependencies=self.analysis.dependencies,
            commands=self.analysis.commands.to_dict(),
            env_info=self.analysis.env_info,
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
        )
```

`src/repoize/generator/claude_md.py`:

```python
        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            languages=self.analysis.languages,
            dependencies=self.analysis.dependencies,
            commands=self.analysis.commands.to_dict(),
            env_info=self.analysis.env_info,
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
        )
```

`src/repoize/generator/cursorrules.py`:

```python
        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            dependencies=self.analysis.dependencies,
            commands=self.analysis.commands.to_dict(),
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
        )
```

`src/repoize/generator/copilot.py`:

```python
        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            commands=self.analysis.commands.to_dict(),
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
        )
```

`src/repoize/generator/mcp_config.py`:

```python
        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            project_path=str(self.analysis.project_path).replace("\\", "/"),
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
        )
```

`src/repoize/generator/skill_md.py`:

```python
        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            dependencies=self.analysis.dependencies,
            commands=self.analysis.commands.to_dict(),
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
        )
```

- [ ] **Step 2: Run existing generator tests**

Run: `python -m pytest tests/test_generators.py -v`
Expected: PASS

- [ ] **Step 3: Commit after user confirmation**

```bash
git add src/repoize/generator
git commit -m "feat: pass profile data to generators"
```

---

### Task 7: 模板改为 profile 驱动

**Files:**
- Modify: `src/repoize/templates/agents_md.j2`
- Modify: `src/repoize/templates/claude_md.j2`
- Modify: `src/repoize/templates/cursorrules.j2`
- Modify: `src/repoize/templates/copilot.j2`
- Modify: `src/repoize/templates/mcp_config.j2`
- Modify: `src/repoize/templates/skill_md.j2`
- Test: `tests/test_generators.py`

- [ ] **Step 1: Add fixture-driven generator tests**

Append to `tests/test_generators.py`:

```python
import pytest


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "languages"

ALL_GENERATORS = [
    AgentsMdGenerator,
    ClaudeMdGenerator,
    CursorRulesGenerator,
    CopilotGenerator,
    SkillMdGenerator,
]


@pytest.mark.parametrize(
    ("language", "setup", "test_cmd"),
    [
        ("javascript", "npm install", "npm run test"),
        ("typescript", "npm install", "npm run test"),
        ("go", "go mod download", "go test ./..."),
        ("rust", "cargo build", "cargo test"),
        ("java", "mvn -q dependency:resolve", "mvn test"),
        ("ruby", "bundle install", "bundle exec rake test"),
        ("php", "composer install", "composer run test"),
    ],
)
def test_non_python_generator_outputs(tmp_path, language, setup, test_cmd):
    fixture = FIXTURE_ROOT / language
    analysis = analyze_project(fixture, scan_env=False)
    assert analysis.profile is not None
    for generator_cls in ALL_GENERATORS:
        content = generator_cls(analysis).generate()
        assert setup in content
        assert test_cmd in content
        assert "pip install" not in content


def test_python_generator_keeps_python_setup():
    analysis = _make_analysis()
    content = AgentsMdGenerator(analysis).generate()
    assert 'pip install -e ".[dev]"' in content


def test_mcp_config_is_generic_for_non_python():
    fixture = FIXTURE_ROOT / "go"
    analysis = analyze_project(fixture, scan_env=False)
    content = McpConfigGenerator(analysis).generate()
    assert "mcpServers" in content
    assert "filesystem" in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_generators.py -v`
Expected: FAIL on fixture-driven tests because templates are still Python-only

- [ ] **Step 3: Replace `agents_md.j2`**

Replace `src/repoize/templates/agents_md.j2` with:

```jinja
# {{ project_name }}

> 本文件由 [repoize](https://github.com/LQDC3417/repoize) 自动生成，请根据项目实际情况调整。

## 项目概述

- **主语言**: {{ primary_language }}{% if profile %}
- **语言画像**: {{ profile.name }}{% endif %}{% if languages | length > 1 %}{% for lang, ratio in languages.items() %}{% if not loop.first %}
- **次要语言**: {{ lang }} ({{ "%.0f" | format(ratio * 100) }}%){% endif %}{% endfor %}{% endif %}

## 技术栈

{% if frameworks %}### 框架
{% for framework in frameworks %}- {{ framework }}
{% endfor %}{% endif %}

### 依赖

{% for dep in dependencies %}{% if not dep.dev %}- {{ dep.name }}{% if dep.version_spec %} ({{ dep.version_spec }}){% endif %}
{% endif %}{% endfor %}

## 开发依赖

{% for dep in dependencies %}{% if dep.dev %}- {{ dep.name }}{% if dep.version_spec %} ({{ dep.version_spec }}){% endif %}
{% endif %}{% endfor %}

{% if profile and profile.setup_commands %}## 快速开始

{% for cmd in profile.setup_commands %}```bash
{{ cmd }}
```
{% endfor %}{% endif %}

## 常用命令

{% if commands.build %}### 构建
{% for cmd in commands.build %}```bash
{{ cmd }}
```
{% endfor %}{% endif %}{% if commands.test %}### 测试
{% for cmd in commands.test %}```bash
{{ cmd }}
```
{% endfor %}{% endif %}{% if commands.lint %}### 代码检查
{% for cmd in commands.lint %}```bash
{{ cmd }}
```
{% endfor %}{% endif %}{% if commands.format %}### 格式化
{% for cmd in commands.format %}```bash
{{ cmd }}
```
{% endfor %}{% endif %}

## 开发环境

{% if env_info.tools %}| 工具 | 版本 |
|------|------|
{% for name, version in env_info.tools %}| {{ name }} | {{ version }} |
{% endfor %}{% endif %}{% if env_info.dev_env_vars %}

### 环境变量

{% for name, value in env_info.dev_env_vars.items() %}- `{{ name }}`: `{{ value }}`
{% endfor %}{% endif %}

## 目录结构

```
{{ project_name }}/
├── src/          # 源代码
├── tests/        # 测试
└── ...
```

## 编码规范

- 代码注释使用中文，变量名和函数名使用英文
- 遵循项目已有代码风格
- 修改代码前先理解现有逻辑，保持最小化改动
- 提交前运行 lint 和测试确保通过
```

- [ ] **Step 4: Replace `claude_md.j2`**

Replace `src/repoize/templates/claude_md.j2` with:

```jinja
# CLAUDE.md — Claude Code 项目指令

> 本文件由 [repoize](https://github.com/LQDC3417/repoize) 自动生成。Claude Code 会自动读取此文件。

## 项目信息

- 项目名: {{ project_name }}
- 主语言: {{ primary_language }}{% if profile %}
- 语言画像: {{ profile.name }}{% endif %}{% if languages | length > 1 %}{% for lang, ratio in languages.items() %}{% if not loop.first %}
- 次要语言: {{ lang }} ({{ "%.0f" | format(ratio * 100) }}%){% endif %}{% endfor %}{% endif %}

## 技术栈

{% if frameworks %}### 框架
{% for framework in frameworks %}- {{ framework }}
{% endfor %}{% endif %}

### 依赖

{% for dep in dependencies %}{% if not dep.dev %}- {{ dep.name }}{% if dep.version_spec %} ({{ dep.version_spec }}){% endif %}
{% endif %}{% endfor %}

{% if profile and profile.setup_commands %}## 快速开始

{% for cmd in profile.setup_commands %}```bash
{{ cmd }}
```
{% endfor %}{% endif %}

{% if commands.build %}## 构建
{% for cmd in commands.build %}```bash
{{ cmd }}
```
{% endfor %}{% endif %}

{% if commands.test %}## 测试
{% for cmd in commands.test %}```bash
{{ cmd }}
```
{% endfor %}{% endif %}

{% if commands.lint %}## 代码检查
{% for cmd in commands.lint %}```bash
{{ cmd }}
```
{% endfor %}{% endif %}

{% if commands.format %}## 格式化
{% for cmd in commands.format %}```bash
{{ cmd }}
```
{% endfor %}{% endif %}

## 开发环境

{% if env_info.tools %}| 工具 | 版本 |
|------|------|
{% for name, version in env_info.tools %}| {{ name }} | {{ version }} |
{% endfor %}{% endif %}{% if env_info.dev_env_vars %}

### 环境变量

{% for name, value in env_info.dev_env_vars.items() %}- `{{ name }}`: `{{ value }}`
{% endfor %}{% endif %}

## 编码规范

- 代码注释使用中文，变量名和函数名使用英文
- 遵循项目已有代码风格，不要随意修改相邻代码的格式
- 修改代码前先理解现有逻辑
- 关键逻辑加注释，简单代码不加注释
- 能用 50 行写完就不要写 200 行
- 优先使用已有的库和工具
- 提交前运行测试和代码检查

## 工作流程

1. 先读懂现有代码再动手修改
2. 改动最小化，不碰无关文件和逻辑
3. 遇到不确定的地方先问用户确认
4. 改完代码后主动跑相关测试验证
5. 不主动 commit，等用户确认后再提交
```

- [ ] **Step 5: Replace `cursorrules.j2`**

Replace `src/repoize/templates/cursorrules.j2` with:

```jinja
# {{ project_name }} — Cursor Rules

# 项目概述
语言: {{ primary_language }}
{% if frameworks %}框架: {{ frameworks | join(", ") }}{% endif %}
{% for dep in dependencies %}{% if not dep.dev %}
依赖: {{ dep.name }}{% endif %}{% endfor %}
{% if profile and profile.setup_commands %}
# 快速开始
{% for cmd in profile.setup_commands %}运行: {{ cmd }}
{% endfor %}{% endif %}

# 编码规范
- 代码注释使用中文，变量名和函数名使用英文
- 遵循项目已有代码风格，不要随意修改相邻代码的格式
- 修改代码前先理解现有逻辑
- 关键逻辑加注释，简单代码不加注释
{% if commands.test %}
# 测试
提交前必须运行: {{ commands.test[0] }}
{% endif %}{% if commands.lint %}
# 代码检查
运行: {{ commands.lint[0] }}
{% endif %}{% if commands.format %}
# 格式化
运行: {{ commands.format[0] }}
{% endif %}
# 原则
- 能用 50 行写完就不要写 200 行
- 优先使用已有的库和工具
- 不要删除未使用的代码，只标记为 TODO
- 不确定的地方先问用户
```

- [ ] **Step 6: Replace `copilot.j2`**

Replace `src/repoize/templates/copilot.j2` with:

```jinja
# {{ project_name }} — Copilot Instructions

> 本文件由 [repoize](https://github.com/LQDC3417/repoize) 自动生成。

## 项目信息

- 语言: {{ primary_language }}
{% if frameworks %}- 框架: {{ frameworks | join(", ") }}
{% endif %}{% if commands.test %}- 测试命令: `{{ commands.test[0] }}`
{% endif %}{% if commands.lint %}- 代码检查: `{{ commands.lint[0] }}`
{% endif %}{% if commands.format %}- 格式化: `{{ commands.format[0] }}`
{% endif %}

{% if profile and profile.setup_commands %}## 快速开始

{% for cmd in profile.setup_commands %}- `{{ cmd }}`
{% endfor %}{% endif %}

## 编码规范

- 代码注释使用中文，变量名和函数名使用英文
- 遵循项目已有代码风格
- 修改代码前先理解现有逻辑
- 关键逻辑加注释，简单代码不加注释
- 能用 50 行写完就不要写 200 行
- 优先使用已有的库和工具

## 提交前检查

{% if commands.lint %}1. 运行 `{{ commands.lint[0] }}` 确保代码检查通过
{% endif %}{% if commands.test %}2. 运行 `{{ commands.test[0] }}` 确保测试通过
{% endif %}{% if commands.format %}3. 运行 `{{ commands.format[0] }}` 确保格式统一
{% endif %}
```

- [ ] **Step 7: Replace `skill_md.j2`**

Replace `src/repoize/templates/skill_md.j2` with:

```jinja
---
name: {{ project_name | lower | replace("_", "-") }}
description: |-
  项目 {{ project_name }} 的开发指南。包含构建、测试、部署的标准流程和编码规范。
license: MIT
---

# {{ project_name }} 开发指南

## 快速开始

{% if profile %}
{% for cmd in profile.setup_commands %}```bash
{{ cmd }}
```
{% endfor %}{% endif %}

## 项目结构

- 主语言: {{ primary_language }}
{% if frameworks %}- 框架: {{ frameworks | join(", ") }}
{% endif %}{% for dep in dependencies %}{% if not dep.dev %}- 依赖: {{ dep.name }}
{% endif %}{% endfor %}

## 编码规范

1. 代码注释使用中文，变量名和函数名使用英文
2. 遵循项目已有代码风格
3. 修改代码前先理解现有逻辑
4. 关键逻辑加注释，简单代码不加注释
5. 能用 50 行写完就不要写 200 行

## 常用命令

{% if commands.build %}### 构建
{% for cmd in commands.build %}- `{{ cmd }}`
{% endfor %}{% endif %}{% if commands.test %}### 测试
{% for cmd in commands.test %}- `{{ cmd }}`
{% endfor %}{% endif %}{% if commands.lint %}### 代码检查
{% for cmd in commands.lint %}- `{{ cmd }}`
{% endfor %}{% endif %}{% if commands.format %}### 格式化
{% for cmd in commands.format %}- `{{ cmd }}`
{% endfor %}{% endif %}
```

- [ ] **Step 8: Replace `mcp_config.j2`**

Replace `src/repoize/templates/mcp_config.j2` with:

```json
{
  "mcpServers": {
    "git": {
      "command": "uvx",
      "args": ["mcp-server-git", "--repository", "{{ project_path }}"]
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "{{ project_path }}"]
    }
  }
}
```

- [ ] **Step 9: Run generator tests**

Run: `python -m pytest tests/test_generators.py -v`
Expected: PASS

- [ ] **Step 10: Commit after user confirmation**

```bash
git add src/repoize/templates tests/test_generators.py
git commit -m "feat: render language-aware agent configs"
```

---

### Task 8: 健康报告显示 profile 和框架

**Files:**
- Modify: `src/repoize/reporter/health_report.py`

- [ ] **Step 1: Add profile/framework lines**

In `print_health_report`, after the language section, add:

```python
    if analysis.profile:
        console.print(f"\n[bold]语言画像:[/bold] {analysis.profile.name}")
    if analysis.frameworks:
        console.print(f"[bold]框架:[/bold] {', '.join(analysis.frameworks)}")
```

- [ ] **Step 2: Run full test suite**

Run: `python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 3: Manual CLI verification**

Run:

```powershell
python -m repoize.cli analyze tests/fixtures/languages/go --no-env
python -m repoize.cli analyze tests/fixtures/languages/php --no-env
```

Expected: output contains `语言画像: Go` / `语言画像: PHP`, and PHP 项目显示 `框架: laravel`

- [ ] **Step 4: Commit after user confirmation**

```bash
git add src/repoize/reporter/health_report.py
git commit -m "feat: show language profile in health report"
```

---

### Task 9: 全量质量检查

**Files:**
- None

- [ ] **Step 1: Run all tests**

Run: `python -m pytest tests/ -v`
Expected: PASS

- [ ] **Step 2: Run lint**

Run: `ruff check src/ tests/`
Expected: PASS

- [ ] **Step 3: Run format check**

Run: `ruff format --check src/ tests/`
Expected: PASS

- [ ] **Step 4: Report completion**

向用户报告：

- 新增和修改的文件清单。
- 多语言 profile 覆盖范围。
- 测试、lint、format 的验证结果。
- 剩余风险和后续建议。

---

## Self-Review Checklist

- [ ] Spec 中“首批 7 种语言”都有 fixture 或 profile。
- [ ] 模板不再只支持 Python quick start。
- [ ] MCP 不再把 Python 作为唯一条件。
- [ ] 每个任务都有失败测试、实现、通过测试和验证命令。
- [ ] 计划中不包含 TODO/TBD 占位。
