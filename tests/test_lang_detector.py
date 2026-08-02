"""语言检测器测试"""

from repoize.analyzer.lang_detector import detect_languages, get_primary_language


def test_detect_python_project(tmp_path):
    """测试 Python 项目检测。"""
    # 创建模拟的 Python 项目
    (tmp_path / "main.py").touch()
    (tmp_path / "utils.py").touch()
    (tmp_path / "models.py").touch()
    (tmp_path / "app.js").touch()

    langs = detect_languages(tmp_path)
    assert "Python" in langs
    assert langs["Python"] > langs.get("JavaScript", 0)


def test_primary_language(tmp_path):
    """测试主语言检测。"""
    (tmp_path / "main.py").touch()
    assert get_primary_language(tmp_path) == "Python"


def test_empty_project(tmp_path):
    """测试空项目。"""
    langs = detect_languages(tmp_path)
    assert len(langs) == 0
    assert get_primary_language(tmp_path) is None
