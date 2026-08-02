"""语言画像注册表：为多语言分析、命令提取和模板渲染提供默认知识。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .dep_parser import DepInfo


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
