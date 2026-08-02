from agentready.analyzer.cmd_extractor import extract_commands
from agentready.analyzer.language_profiles import get_language_profile


def test_go_profile_fills_default_commands(tmp_path):
    (tmp_path / "go.mod").write_text("module example.com/foo\n\ngo 1.22\n", encoding="utf-8")
    cmds = extract_commands(tmp_path, profile=get_language_profile("Go"))
    assert "go build ./..." in cmds.build
    assert "go test ./..." in cmds.test
    assert "gofmt -w ." in cmds.format


def test_package_scripts_take_priority(tmp_path):
    content = """{
  "scripts": {
    "build": "vite build",
    "test": "vitest run",
    "lint": "eslint ."
  }
}
"""
    (tmp_path / "package.json").write_text(content, encoding="utf-8")
    cmds = extract_commands(tmp_path, profile=get_language_profile("JavaScript"))
    assert "npm run build" in cmds.build
    assert "npm run lint" in cmds.lint


def test_java_maven_commands(tmp_path):
    (tmp_path / "pom.xml").write_text("<project></project>", encoding="utf-8")
    cmds = extract_commands(tmp_path, profile=get_language_profile("Java"))
    assert "mvn verify" in cmds.build
    assert "mvn test" in cmds.test


def test_php_composer_scripts(tmp_path):
    content = """{
  "scripts": {
    "test": "phpunit",
    "lint": "php-cs-fixer check"
  }
}
"""
    (tmp_path / "composer.json").write_text(content, encoding="utf-8")
    cmds = extract_commands(tmp_path, profile=get_language_profile("PHP"))
    assert "composer run test" in cmds.test
    assert "composer run lint" in cmds.lint
