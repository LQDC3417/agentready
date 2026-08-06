"""CLAUDE.md 生成器"""

from . import get_template_env
from .base import BaseGenerator


class ClaudeMdGenerator(BaseGenerator):
    """生成 CLAUDE.md 文件（Claude Code 专属指令）。"""

    @property
    def name(self) -> str:
        """生成器名称。"""
        return "CLAUDE.md"

    @property
    def output_filename(self) -> str:
        """输出文件名。"""
        return "CLAUDE.md"

    def generate(self) -> str:
        """生成文件内容。"""
        env = get_template_env()
        template = env.get_template("claude_md.j2")

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
