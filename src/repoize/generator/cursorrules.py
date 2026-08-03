""".cursorrules 生成器"""

from . import get_template_env
from .base import BaseGenerator


class CursorRulesGenerator(BaseGenerator):
    """生成 .cursorrules 文件。"""

    @property
    def name(self) -> str:
        return ".cursorrules"

    @property
    def output_filename(self) -> str:
        return ".cursorrules"

    def generate(self) -> str:
        env = get_template_env()
        template = env.get_template("cursorrules.j2")

        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            dependencies=self.analysis.dependencies,
            commands=self.analysis.commands.to_dict(),
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
        )
