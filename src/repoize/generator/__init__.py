"""生成器模块"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

_TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
_env: Environment | None = None


def get_template_env() -> Environment:
    """返回共享的 Jinja2 Environment 实例（惰性初始化）。"""
    global _env
    if _env is None:
        _env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)))
    return _env
