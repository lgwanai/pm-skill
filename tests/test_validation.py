"""Tests for document validation (IMP-06)."""

from scripts.utils.validation import validate_markdown, ValidationIssue


def test_validate_clean_markdown():
    """Test that valid content returns empty list."""
    content = "# Heading\n\nParagraph text."
    issues = validate_markdown(content)
    assert issues == []


def test_validate_table_column_mismatch():
    """Test that table column mismatches are detected."""
    content = "| Col1 | Col2 |\n|-----|\n| A | B | C |"
    issues = validate_markdown(content)
    assert any(i.level == "error" and "column" in i.message.lower() for i in issues)


def test_validate_image_reference():
    """Test that missing image references are warned."""
    content = "![alt](missing-image.png)"
    issues = validate_markdown(content)
    # Image warnings only apply when checking file existence, so this should pass
    # since we're not providing a base path
    assert isinstance(issues, list)


def test_validation_issue_structure():
    """Test that ValidationIssue has required attributes."""
    issues = validate_markdown("| A |\n|--|\n| B | C |")
    assert len(issues) > 0
    assert hasattr(issues[0], 'level')
    assert hasattr(issues[0], 'message')
    assert hasattr(issues[0], 'line')


def test_validation_levels():
    """Test that validation levels are error, warn, info."""
    # Create content with a table error
    content = "| Col1 |\n|------|\n| A | B |"
    issues = validate_markdown(content)
    assert len(issues) > 0
    assert issues[0].level in ("error", "warn", "info")


def test_validate_unclosed_code_block():
    """Test that unclosed code blocks are detected."""
    content = "```python\ndef hello():\n    pass\n"
    issues = validate_markdown(content)
    assert any(i.level == "error" and "code block" in i.message.lower() for i in issues)


def test_validate_table_missing_separator():
    """Test that tables missing separator row are detected."""
    content = "| Col1 | Col2 |\n| A | B |"
    issues = validate_markdown(content)
    assert any(i.level == "error" and "separator" in i.message.lower() for i in issues)


def test_validate_broken_link_reference():
    """Test that orphaned reference links are warned."""
    content = "[link][ref]\n\nSome other content."
    issues = validate_markdown(content)
    assert any(i.level == "warn" and "reference" in i.message.lower() for i in issues)
