"""Copilot 指令生成器"""

from . import get_template_env
from .base import BaseGenerator


class CopilotGenerator(BaseGenerator):
    """生成 .github/copilot-instructions.md 文件。"""

    @property
    def name(self) -> str:
        return "copilot-instructions.md"

    @property
    def output_filename(self) -> str:
        return ".github/copilot-instructions.md"

    def generate(self) -> str:
        env = get_template_env()
        template = env.get_template("copilot.j2")

        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            commands=self.analysis.commands.to_dict(),
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
        )
