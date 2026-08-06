"""MCP Server 配置生成器"""

from . import get_template_env
from .base import BaseGenerator


class McpConfigGenerator(BaseGenerator):
    """生成 MCP Server 配置文件。"""

    @property
    def name(self) -> str:
        """生成器名称。"""
        return "MCP 配置"

    @property
    def output_filename(self) -> str:
        """输出文件名。"""
        return ".claude/mcp.json"

    def generate(self) -> str:
        """生成文件内容。"""
        env = get_template_env()
        template = env.get_template("mcp_config.j2")

        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            project_path=str(self.analysis.project_path).replace("\\", "/"),
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
        )
