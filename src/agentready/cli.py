"""CLI 入口 — click 命令组"""

from pathlib import Path

import click
from rich.console import Console
from rich.prompt import Confirm

from .analyzer.project_analyzer import analyze_project
from .reporter.health_report import print_health_report

console = Console()

# 生成器类型到模块的映射
GENERATOR_MAP = {
    "agents": ("generator.agents_md", "AgentsMdGenerator"),
    "claude": ("generator.claude_md", "ClaudeMdGenerator"),
    "cursorrules": ("generator.cursorrules", "CursorRulesGenerator"),
    "copilot": ("generator.copilot", "CopilotGenerator"),
    "mcp": ("generator.mcp_config", "McpConfigGenerator"),
    "skill": ("generator.skill_md", "SkillMdGenerator"),
}


def _load_generator(name: str, analysis):
    """动态加载生成器类。"""
    import importlib
    module_path, class_name = GENERATOR_MAP[name]
    module = importlib.import_module(f"agentready.{module_path}")
    cls = getattr(module, class_name)
    return cls(analysis)


@click.group()
@click.version_option(package_name="agentready")
def main():
    """agentready — 一条命令让任何项目对 AI Agent 友好。

    自动生成 AGENTS.md、CLAUDE.md、.cursorrules、MCP 配置、Skill 文件，
    让 Claude Code、Cursor、Copilot 等 AI 编程助手立即理解你的项目。
    """
    pass


@main.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--force", is_flag=True, help="覆盖已有配置文件")
@click.option("--no-env", is_flag=True, help="跳过环境变量扫描")
def init(path, force, no_env):
    """扫描项目并一键生成所有 Agent 配置文件。"""
    project_path = Path(path).resolve()
    console.print(f"[bold blue]🔍 正在扫描项目:[/bold blue] {project_path}")

    if not no_env:
        console.print("[dim]📡 扫描开发环境...[/dim]")

    # 分析项目
    analysis = analyze_project(project_path, scan_env=not no_env)
    print_health_report(analysis, console)

    # 检查已有配置
    existing = [c for c in analysis.existing_configs if c.exists]
    if existing and not force:
        console.print(f"[yellow]⚠️  检测到 {len(existing)} 个已有配置文件。[/yellow]")
        for c in existing:
            console.print(f"  - {c.name}")
        if not Confirm.ask("是否继续？已有文件将被跳过"):
            console.print("[dim]已取消。[/dim]")
            return

    # 生成所有配置文件
    console.print("\n[bold]⚙️  开始生成配置文件...[/bold]\n")
    generated = []
    skipped = []

    for gen_name in GENERATOR_MAP:
        gen = _load_generator(gen_name, analysis)
        output_path = project_path / gen.output_filename

        if output_path.exists() and not force:
            skipped.append(gen.output_filename)
            console.print(f"  [yellow]⏭  跳过 {gen.output_filename}（已存在）[/yellow]")
            continue

        try:
            result_path = gen.write(project_path, force=force)
            generated.append(gen.output_filename)
            console.print(f"  [green]✅ 生成 {gen.output_filename}[/green]")
        except Exception as e:
            console.print(f"  [red]❌ 生成 {gen.output_filename} 失败: {e}[/red]")

    # 汇总
    console.print(f"\n[bold green]✅ 完成！生成 {len(generated)} 个文件[/bold green]")
    if skipped:
        console.print(f"[yellow]⏭  跳过 {len(skipped)} 个已存在文件（使用 --force 覆盖）[/yellow]")


@main.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--format", "output_format", default="terminal",
              type=click.Choice(["terminal", "html"]),
              help="输出格式")
@click.option("--no-env", is_flag=True, help="跳过环境变量扫描")
def analyze(path, output_format, no_env):
    """分析项目结构并输出健康度报告（不生成文件）。"""
    project_path = Path(path).resolve()
    console.print(f"[bold blue]📊 正在分析项目:[/bold blue] {project_path}")

    analysis = analyze_project(project_path, scan_env=not no_env)

    if output_format == "terminal":
        print_health_report(analysis, console)
    else:
        console.print("[yellow]⚠️  HTML 输出功能开发中...[/yellow]")


@main.command()
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--type", "file_types", multiple=True,
              type=click.Choice(["agents", "claude", "cursorrules", "copilot", "mcp", "skill"]),
              help="要生成的配置文件类型（可多次指定）")
@click.option("--force", is_flag=True, help="覆盖已有配置文件")
@click.option("--no-env", is_flag=True, help="跳过环境变量扫描")
def generate(path, file_types, force, no_env):
    """选择性生成指定类型的配置文件。"""
    if not file_types:
        console.print("[red]请至少指定一个文件类型，例如: --type agents --type mcp[/red]")
        console.print("\n可用类型:")
        for name in GENERATOR_MAP:
            console.print(f"  - {name}")
        raise SystemExit(1)

    project_path = Path(path).resolve()
    console.print(f"[bold blue]⚙️  正在生成配置:[/bold blue] {', '.join(file_types)}")

    analysis = analyze_project(project_path, scan_env=not no_env)

    for gen_name in file_types:
        gen = _load_generator(gen_name, analysis)
        output_path = project_path / gen.output_filename

        if output_path.exists() and not force:
            console.print(f"  [yellow]⏭  跳过 {gen.output_filename}（已存在，使用 --force 覆盖）[/yellow]")
            continue

        try:
            result_path = gen.write(project_path, force=force)
            console.print(f"  [green]✅ 生成 {gen.output_filename}[/green]")
        except Exception as e:
            console.print(f"  [red]❌ 生成 {gen.output_filename} 失败: {e}[/red]")


@main.command()
@click.argument("path", default=".", type=click.Path(exists=True))
def check(path):
    """检查项目是否已具备 Agent 友好配置。"""
    project_path = Path(path).resolve()
    console.print(f"[bold blue]✅ 正在检查项目:[/bold blue] {project_path}")

    analysis = analyze_project(project_path)
    print_health_report(analysis, console)

    # 给出建议
    score = analysis.agent_ready_score
    if score >= 80:
        console.print("[bold green]🎉 你的项目已经对 AI Agent 非常友好了！[/bold green]")
    elif score >= 40:
        console.print("[bold yellow]💡 建议运行 'agentready init' 补充缺失的配置文件。[/bold yellow]")
    else:
        console.print("[bold red]🚀 建议运行 'agentready init' 一键生成所有配置文件。[/bold red]")


if __name__ == "__main__":
    main()
