"""MCP Server 配置生成器"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .base import BaseGenerator


class McpConfigGenerator(BaseGenerator):
    """生成 MCP Server 配置文件。"""

    @property
    def name(self) -> str:
        return "MCP 配置"

    @property
    def output_filename(self) -> str:
        return ".claude/mcp.json"

    def generate(self) -> str:
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("mcp_config.j2")

        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            project_path=str(self.analysis.project_path).replace("\\", "/"),
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
        )
