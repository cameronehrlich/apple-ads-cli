"""Source-distribution content contract tests."""

from pathlib import Path


def test_manifest_in_includes_public_skill_and_release_files():
    manifest = Path("MANIFEST.in").read_text().splitlines()

    assert "include CONTRIBUTING.md" in manifest
    assert "include RELEASING.md" in manifest
    assert "include SKILL.md" in manifest
    assert "recursive-include agents *.yaml" in manifest
    assert "recursive-include references *.md" in manifest
    assert "recursive-include scripts *.py" in manifest
