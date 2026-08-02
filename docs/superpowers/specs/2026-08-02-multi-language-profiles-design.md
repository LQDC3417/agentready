# Multi-Language Profiles Design

- 日期：2026-08-02
- 状态：待用户审查
- 项目：repoize

## 1. 背景

当前 `repoize` 的完整能力集中在 Python 项目：

- 语言检测支持 30+ 种语言。
- 依赖解析和命令提取只完整覆盖 Python、JS/TS、Go、Rust。
- 模板中硬编码了 Python 的安装方式，例如 `pip install -e ".[dev]"`。
- `SKILL.md` 模板只在 Python 分支下生成 quick start。
- MCP 配置只对 Python 项目额外生成 filesystem server。

本设计把范围扩到多语言宽覆盖，让非 Python 项目也能生成基础可用的 Agent 配置。

## 2. 目标

- Python 保持现有完整支持，不产生行为回归。
- 首批新增 JavaScript、TypeScript、Go、Rust、Java、Ruby、PHP 的基础支持。
- 识别语言对应的 manifest、依赖、框架和常用命令。
- 6 个生成器改为数据驱动，不再把 Python 命令硬编码进所有语言。
- 每种语言有独立 fixture 测试，验证分析和生成结果。

## 3. 非目标

- 不做深度框架级生成。
- 不做外部模板插件或用户自定义语言包。
- 不做 HTML report。
- 不做 PyPI 发布相关改造。
- 不改变现有模板的中文编码规范风格。

## 4. 架构

新增语言 profile 层，放在 analyzer 与模板之间：

```text
analyzer -> LanguageProfile registry -> ProjectAnalysis.profile/frameworks
                                              |
                                              v
                          AGENTS/CLAUDE/Cursor/Copilot/SKILL/MCP templates
```

Analyzer 负责收集项目事实，profile 负责提供语言默认知识，模板负责渲染。

## 5. LanguageProfile 数据模型

新增文件：`src/repoize/analyzer/language_profiles.py`

```python
@dataclass
class LanguageProfile:
    name: str
    manifest_files: tuple[str, ...]
    setup_commands: tuple[str, ...]
    commands: dict[str, tuple[str, ...]]
    framework_keywords: tuple[str, ...]
```

字段含义：

- `name`：profile 对应的主语言名，例如 `JavaScript`。
- `manifest_files`：需要识别的项目文件，例如 `package.json`。
- `setup_commands`：快速开始命令，例如 `npm install`。
- `commands`：build/test/lint/format/run 的默认命令兜底。
- `framework_keywords`：用于从依赖名中识别框架。

注册表提供：

```python
def get_language_profile(language: str | None) -> LanguageProfile | None:
    ...
```

没有匹配 profile 时返回 `None`，保持通用 fallback。

## 6. Analyzer 集成

修改文件：`src/repoize/analyzer/project_analyzer.py`

`ProjectAnalysis` 增加字段：

```python
profile: LanguageProfile | None
frameworks: list[str]
```

`analyze_project()` 流程：

1. 通过 `detect_languages()` 得到主语言。
2. 通过 `get_language_profile()` 匹配 profile。
3. 调用 `parse_dependencies(project_path, profile=profile)`。
4. 调用 `extract_commands(project_path, profile=profile)`。
5. 调用新增的 `detect_frameworks(profile, dependencies)`。
6. 把 `profile`、`frameworks` 写入 `ProjectAnalysis`。

`parse_dependencies()` 和 `extract_commands()` 的 `profile` 参数都是可选的：

- 传 `profile` 时优先使用 profile 指定的 manifest 和默认命令。
- 不传时保持当前逻辑不变。

## 7. Manifest 与依赖解析

修改文件：`src/repoize/analyzer/dep_parser.py`

| 语言 | Manifest | 解析方式 |
|------|----------|----------|
| JavaScript/TypeScript | `package.json` | 现有 JSON 解析 |
| Go | `go.mod` | 现有文本解析 |
| Rust | `Cargo.toml` | 现有 TOML 文本解析 |
| Java | `pom.xml` | Python 标准库 XML parser |
| Java | `build.gradle` | 保守提取 `implementation`/`api` 依赖 |
| Ruby | `Gemfile` | 提取 `gem` 声明 |
| PHP | `composer.json` | Python 标准库 JSON parser |

## 8. 默认命令

修改文件：`src/repoize/analyzer/cmd_extractor.py`

| 语言 | Setup | Build | Test | Lint | Format |
|------|-------|-------|------|------|--------|
| JS/TS | `npm install` | 优先 package scripts | `npm test` | `npm run lint` | `npm run format` |
| Go | `go mod download` | `go build ./...` | `go test ./...` | `golangci-lint run` | `gofmt -w .` |
| Rust | `cargo build` | `cargo build` | `cargo test` | `cargo clippy -- -D warnings` | `cargo fmt --check` |
| Java | `mvn`/`gradle` 对应命令 | `mvn verify`/`gradle build` | `mvn test`/`gradle test` | `mvn checkstyle:check`/`gradle check` | 不伪造格式命令 |
| Ruby | `bundle install` | `bundle exec rake build` | `bundle exec rake test` | `bundle exec rubocop` | 不伪造格式命令 |
| PHP | `composer install` | 优先 composer scripts | `vendor/bin/phpunit` | `vendor/bin/php-cs-fixer check` | `vendor/bin/php-cs-fixer fix` |

命令优先级：

1. 项目 manifest 或配置中明确存在的脚本/目标。
2. profile 提供的默认命令。
3. 都没有时保持该分类为空，不生成错误命令。

## 9. 框架识别

新增函数：`detect_frameworks(profile, dependencies)`

用 `dependencies` 中的包名匹配 `profile.framework_keywords`，输出稳定且可测试的框架名。

首版关键词示例：

- JS/TS：`next`、`react`、`express`、`vue`、`svelte`、`astro`
- Go：`gin`、`echo`、`fiber`
- Rust：`axum`、`actix-web`、`rocket`
- Java：`spring-boot`、`spring-web`、`quarkus`
- Ruby：`rails`、`sinatra`
- PHP：`laravel`、`symfony`

## 10. 模板改造

修改 6 个模板文件，并为所有生成器传入 `profile` 和 `frameworks`：

- `src/repoize/templates/agents_md.j2`
- `src/repoize/templates/claude_md.j2`
- `src/repoize/templates/cursorrules.j2`
- `src/repoize/templates/copilot.j2`
- `src/repoize/templates/skill_md.j2`
- `src/repoize/templates/mcp_config.j2`

同时修改 6 个生成器文件，把 `profile` 和 `frameworks` 传给模板。

具体行为：

1. `AGENTS.md`、`CLAUDE.md`：技术栈增加框架列表，quick start 使用 `profile.setup_commands`。
2. `.cursorrules`、Copilot 指令：命令来源改为 `commands` 和 `profile`。
3. `SKILL.md`：用 profile 分支替换 `if primary_language == "Python"`。
4. MCP 配置：改为通用本地项目 `git + filesystem`，不再以 Python 作为唯一条件。
5. 现有 Python 输出尽量保持不变。

## 11. 测试

新增 fixture 目录：

```text
tests/fixtures/languages/
├── javascript/
├── typescript/
├── go/
├── rust/
├── java/
├── ruby/
└── php/
```

新增或修改测试：

- `tests/test_language_profiles.py`：profile 匹配、框架识别、默认命令兜底。
- `tests/test_dep_parser.py`：新增 Java/Ruby/PHP manifest 解析。
- `tests/test_cmd_extractor.py`：项目脚本优先，profile 命令兜底。
- `tests/test_generators.py`：每种语言生成 6 类文件，断言不含 Python 专用内容。

## 12. 验收条件

- `pytest` 全绿。
- `ruff check src/ tests/` 通过。
- `ruff format --check src/ tests/` 通过。
- 现有 Python 测试继续通过。
- 对 JS/Go/Rust fixture 手动运行 `repoize analyze` 和 `repoize init`，结果语言正确。

## 13. 风险与假设

- Java 的 `build.gradle` 是 Groovy/Kotlin DSL，文本解析只能覆盖常见依赖写法。
- JS/TS 可能使用 `npm`、`pnpm`、`yarn` 或 `bun`，首版以 `npm` 为默认，不做自动包管理器切换。
- 模板输出语言保持中文，暂不做多语言模板。
- fixture 为静态文件，测试不执行真实安装命令。

## 14. 后续方向

- 深度框架模板和项目结构模板。
- 包管理器自动识别。
- MCP Server 自动发现。
- 用户自定义模板。
- HTML report。
