"""Tests for SKILL.md frontmatter and structure (FND-01)."""

from pathlib import Path


def test_skill_md_exists():
    """Check SKILL.md file exists."""
    assert Path("SKILL.md").exists()


def test_skill_md_frontmatter_name():
    """Check frontmatter has name field."""
    content = Path("SKILL.md").read_text()
    assert "name: pm-skill" in content


def test_skill_md_frontmatter_description():
    """Check frontmatter has description field."""
    content = Path("SKILL.md").read_text()
    assert "description:" in content


def test_skill_md_has_commands():
    """Check SKILL.md documents available commands."""
    content = Path("SKILL.md").read_text()
    assert "init" in content
    assert "config" in content
    assert "import" in content
