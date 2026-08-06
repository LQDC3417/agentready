from repoize.analyzer.dep_parser import DepInfo
from repoize.analyzer.language_profiles import detect_frameworks, get_language_profile


def test_get_language_profile_go():
    profile = get_language_profile("Go")
    assert profile is not None
    assert profile.manifest_files == ("go.mod", "go.sum")
    assert "go test ./..." in profile.commands["test"]


def test_get_language_profile_unknown():
    assert get_language_profile("Unknown") is None
    assert get_language_profile(None) is None


def test_detect_frameworks_go():
    profile = get_language_profile("Go")
    deps = [DepInfo("gin"), DepInfo("gorm")]
    frameworks = detect_frameworks(profile, deps)
    assert "gin" in frameworks
    assert "gorm" in frameworks


def test_detect_frameworks_empty():
    profile = get_language_profile("Rust")
    deps = [DepInfo("serde")]
    frameworks = detect_frameworks(profile, deps)
    # serde is now a framework keyword for Rust
    assert "serde" in frameworks
