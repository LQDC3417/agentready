"""SKILL.md 生成器"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .base import BaseGenerator


class SkillMdGenerator(BaseGenerator):
    """生成项目专属 SKILL.md 文件。"""

    @property
    def name(self) -> str:
        return "SKILL.md"

    @property
    def output_filename(self) -> str:
        return ".claude/skills/project-dev/SKILL.md"

    def generate(self) -> str:
        template_dir = Path(__file__).parent.parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("skill_md.j2")

        return template.render(
            project_name=self.analysis.project_name,
            primary_language=self.analysis.primary_language or "Unknown",
            dependencies=self.analysis.dependencies,
            commands=self.analysis.commands.to_dict(),
            profile=self.analysis.profile,
            frameworks=self.analysis.frameworks,
        )
