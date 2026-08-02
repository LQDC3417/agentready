from agentready.analyzer.dep_parser import DepInfo
from agentready.analyzer.language_profiles import detect_frameworks, get_language_profile


def test_get_language_profile_go():
    profile = get_language_profile("Go")
    assert profile is not None
    assert profile.manifest_files == ("go.mod",)
    assert "go test ./..." in profile.commands["test"]


def test_get_language_profile_unknown():
    assert get_language_profile("Unknown") is None
    assert get_language_profile(None) is None


def test_detect_frameworks_go():
    profile = get_language_profile("Go")
    deps = [DepInfo("gin"), DepInfo("gorm")]
    assert detect_frameworks(profile, deps) == ["gin"]


def test_detect_frameworks_empty():
    profile = get_language_profile("Rust")
    deps = [DepInfo("serde")]
    assert detect_frameworks(profile, deps) == []
