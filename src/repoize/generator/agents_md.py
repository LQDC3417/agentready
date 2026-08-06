"""AGENTS.md 生成器"""

from . import get_template_env
from .base import BaseGenerator


class AgentsMdGenerator(BaseGenerator):
    """生成 AGENTS.md 文件。"""

    @property
    def name(self) -> str:
        """生成器名称。"""
        return "AGENTS.md"

    @property
    def output_filename(self) -> str:
        """输出文件名。"""
        return "AGENTS.md"

    def generate(self) -> str:
        """生成文件内容。"""
        env = get_template_env()
        template = env.get_template("agents_md.j2")

        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            languages=self.analysis.languages,
            dependencies=self.analysis.dependencies,
            commands=self.analysis.commands.to_dict(),
            env_info=self.analysis.env_info,
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
            directory_tree=self.analysis.directory_tree,
        )
