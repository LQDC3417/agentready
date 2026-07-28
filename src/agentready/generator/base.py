"""生成器基类"""

from abc import ABC, abstractmethod
from pathlib import Path

from ..analyzer.project_analyzer import ProjectAnalysis


class BaseGenerator(ABC):
    """配置文件生成器基类。"""

    def __init__(self, analysis: ProjectAnalysis):
        self.analysis = analysis

    @property
    @abstractmethod
    def name(self) -> str:
        """生成器名称。"""
        ...

    @property
    @abstractmethod
    def output_filename(self) -> str:
        """输出文件名（相对项目根目录）。"""
        ...

    @abstractmethod
    def generate(self) -> str:
        """生成文件内容。返回 Markdown/JSON 文本。"""
        ...

    def write(self, project_path: Path, force: bool = False) -> Path:
        """将生成的内容写入文件。返回写入路径。"""
        output_path = project_path / self.output_filename

        if output_path.exists() and not force:
            raise FileExistsError(
                f"{output_path} 已存在。使用 --force 覆盖。"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        content = self.generate()
        output_path.write_text(content, encoding="utf-8")
        return output_path
