"""AGENTS.md 生成器"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .base import BaseGenerator


class AgentsMdGenerator(BaseGenerator):
    """生成 AGENTS.md 文件。"""

    @property
    def name(self) -> str:
        return "AGENTS.md"

    @property
    def output_filename(self) -> str:
        return "AGENTS.md"

    def generate(self) -> str:
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("agents_md.j2")

        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            languages=self.analysis.languages,
            dependencies=self.analysis.dependencies,
            commands=self.analysis.commands.to_dict(),
            env_info=self.analysis.env_info,
        )
