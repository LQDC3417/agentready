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
    quality_tools: tuple[str, ...] = ()  # 代码质量工具


PROFILES: tuple[LanguageProfile, ...] = (
    LanguageProfile(
        name="Python",
        manifest_files=("pyproject.toml", "requirements.txt", "requirements-dev.txt", "setup.py", "setup.cfg"),
        setup_commands=('pip install -e ".[dev]"',),
        commands={
            "build": ("python -m build",),
            "test": ("pytest",),
            "lint": ("ruff check .",),
            "format": ("ruff format .",),
            "type-check": ("mypy .",),
            "coverage": ("pytest --cov",),
        },
        framework_keywords=(
            "fastapi",
            "django",
            "flask",
            "sqlalchemy",
            "pydantic",
            "celery",
            "pytest",
            "black",
            "isort",
            "mypy",
        ),
        quality_tools=("ruff", "mypy", "pylint", "flake8", "bandit"),
    ),
    LanguageProfile(
        name="JavaScript",
        manifest_files=("package.json",),
        setup_commands=("npm install",),
        commands={
            "build": ("npm run build",),
            "test": ("npm test",),
            "lint": ("npm run lint",),
            "format": ("npm run format",),
            "dev": ("npm run dev",),
            "start": ("npm start",),
        },
        framework_keywords=(
            "next",
            "react",
            "vue",
            "svelte",
            "astro",
            "nuxt",
            "express",
            "fastify",
            "koa",
            "nestjs",
            "angular",
            "webpack",
            "vite",
            "rollup",
            "esbuild",
            "turbo",
        ),
        quality_tools=("eslint", "prettier", "jest", "vitest"),
    ),
    LanguageProfile(
        name="TypeScript",
        manifest_files=("package.json", "tsconfig.json"),
        setup_commands=("npm install",),
        commands={
            "build": (
                "npm run build",
                "tsc",
            ),
            "test": ("npm test",),
            "lint": ("npm run lint",),
            "format": ("npm run format",),
            "dev": ("npm run dev",),
            "type-check": ("tsc --noEmit",),
        },
        framework_keywords=(
            "next",
            "react",
            "vue",
            "svelte",
            "astro",
            "nuxt",
            "express",
            "fastify",
            "koa",
            "nestjs",
            "angular",
            "webpack",
            "vite",
            "rollup",
            "esbuild",
            "turbo",
            "prisma",
            "trpc",
            "zod",
            "tailwindcss",
        ),
        quality_tools=("eslint", "prettier", "jest", "vitest", "typescript"),
    ),
    LanguageProfile(
        name="Go",
        manifest_files=("go.mod", "go.sum"),
        setup_commands=("go mod download",),
        commands={
            "build": ("go build ./...",),
            "test": ("go test ./...",),
            "lint": ("golangci-lint run",),
            "format": ("gofmt -w .",),
            "vet": ("go vet ./...",),
            "tidy": ("go mod tidy",),
        },
        framework_keywords=("gin", "echo", "fiber", "chi", "mux", "gorilla", "gorm", "ent", "sqlx", "cobra", "viper"),
        quality_tools=("golangci-lint", "gofmt", "goimports"),
    ),
    LanguageProfile(
        name="Rust",
        manifest_files=("Cargo.toml", "Cargo.lock"),
        setup_commands=("cargo build",),
        commands={
            "build": ("cargo build",),
            "test": ("cargo test",),
            "lint": ("cargo clippy -- -D warnings",),
            "format": ("cargo fmt --check",),
            "bench": ("cargo bench",),
            "doc": ("cargo doc --open",),
        },
        framework_keywords=("axum", "actix-web", "rocket", "warp", "tower", "tokio", "serde", "diesel", "sqlx", "clap"),
        quality_tools=("cargo-clippy", "cargo-fmt", "cargo-audit"),
    ),
    LanguageProfile(
        name="Java",
        manifest_files=("pom.xml", "build.gradle", "build.gradle.kts"),
        setup_commands=("mvn -q dependency:resolve",),
        commands={
            "build": (
                "mvn verify",
                "gradle build",
            ),
            "test": (
                "mvn test",
                "gradle test",
            ),
            "lint": (
                "mvn checkstyle:check",
                "gradle checkstyleMain",
            ),
            "format": (
                "mvn spotless:apply",
                "gradle spotlessApply",
            ),
            "package": (
                "mvn package",
                "gradle bootJar",
            ),
        },
        framework_keywords=(
            "spring-boot",
            "spring-web",
            "spring-data",
            "spring-security",
            "quarkus",
            "micronaut",
            "hibernate",
            "mybatis",
            "jackson",
        ),
        quality_tools=("checkstyle", "spotbugs", "pmd", "spotless"),
    ),
    LanguageProfile(
        name="Ruby",
        manifest_files=("Gemfile", "Gemfile.lock", "Rakefile"),
        setup_commands=("bundle install",),
        commands={
            "build": ("bundle exec rake build",),
            "test": (
                "bundle exec rspec",
                "bundle exec rake test",
            ),
            "lint": ("bundle exec rubocop",),
            "format": ("bundle exec rubocop -A",),
            "console": ("bundle exec rails console",),
        },
        framework_keywords=(
            "rails",
            "sinatra",
            "hanami",
            "rspec",
            "minitest",
            "sidekiq",
            "devise",
            "pundit",
            "activeadmin",
        ),
        quality_tools=("rubocop", "brakeman", "bundler-audit"),
    ),
    LanguageProfile(
        name="PHP",
        manifest_files=("composer.json", "composer.lock"),
        setup_commands=("composer install",),
        commands={
            "test": ("vendor/bin/phpunit",),
            "lint": ("vendor/bin/php-cs-fixer check",),
            "format": ("vendor/bin/php-cs-fixer fix",),
            "stan": ("vendor/bin/phpstan analyse",),
            "serve": ("php artisan serve",),
        },
        framework_keywords=("laravel", "symfony", "codeigniter", "cakephp", "phpunit", "pest", "phpstan", "psalm"),
        quality_tools=("php-cs-fixer", "phpstan", "psalm", "phpunit"),
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


def detect_quality_tools(profile: LanguageProfile | None, dependencies: list[DepInfo]) -> list[str]:
    """根据依赖名识别 profile 中的代码质量工具。"""
    if profile is None:
        return []
    names = [dep.name.lower() for dep in dependencies]
    found: list[str] = []
    for tool in profile.quality_tools:
        if any(tool in name for name in names):
            found.append(tool)
    return found
