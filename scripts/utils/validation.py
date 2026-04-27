"""Markdown validation utilities (IMP-06)."""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ValidationIssue:
    """Represents a validation issue found in Markdown content."""
    level: str  # "error", "warn", "info"
    message: str
    line: int


def validate_markdown(
    content: str,
    base_path: Path | None = None,
) -> list[ValidationIssue]:
    """Validate Markdown content for common issues.

    Checks:
    - Table syntax: column count consistency, separator row format
    - Image references: warn if local path doesn't exist (when base_path provided)
    - Format integrity: unclosed code blocks, orphaned reference links

    Args:
        content: Markdown content to validate
        base_path: Optional base path for resolving image references

    Returns:
        List of ValidationIssue objects (empty if content is valid)
    """
    issues: list[ValidationIssue] = []
    lines = content.split("\n")

    # Track code block state
    in_code_block = False
    code_block_start = 0

    # Track reference-style links
    references_defined: set[str] = set()
    references_used: set[str] = set()

    # Parse reference definitions first
    ref_def_pattern = re.compile(r"^\[([^\]]+)\]:\s*\S+")
    for i, line in enumerate(lines, 1):
        match = ref_def_pattern.match(line)
        if match:
            references_defined.add(match.group(1).lower())

    for i, line in enumerate(lines, 1):
        # Check code blocks
        if line.strip().startswith("```"):
            if not in_code_block:
                in_code_block = True
                code_block_start = i
            else:
                in_code_block = False

        if in_code_block:
            continue

        # Check tables
        if "|" in line and not line.strip().startswith("#"):
            issues.extend(_validate_table_line(line, lines, i))

        # Check image references
        img_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
        for match in img_pattern.finditer(line):
            img_path = match.group(2)
            if base_path and not img_path.startswith(("http://", "https://", "/")):
                full_path = base_path / img_path
                if not full_path.exists():
                    issues.append(ValidationIssue(
                        level="warn",
                        message=f"Image reference '{img_path}' not found",
                        line=i,
                    ))

        # Track reference-style link usage
        ref_link_pattern = re.compile(r"\[([^\]]+)\]\[([^\]]*)\]")
        for match in ref_link_pattern.finditer(line):
            ref_id = match.group(2) or match.group(1)
            references_used.add(ref_id.lower())

    # Check for unclosed code block
    if in_code_block:
        issues.append(ValidationIssue(
            level="error",
            message=f"Unclosed code block starting at line {code_block_start}",
            line=code_block_start,
        ))

    # Check for orphaned references
    for ref in references_used:
        if ref not in references_defined:
            issues.append(ValidationIssue(
                level="warn",
                message=f"Orphaned link reference '{ref}'",
                line=1,
            ))

    return issues


def _validate_table_line(
    line: str,
    all_lines: list[str],
    line_num: int,
) -> list[ValidationIssue]:
    """Validate a single table line.

    Checks:
    - Column count consistency
    - Separator row format

    Args:
        line: The line to validate
        all_lines: All lines in the document
        line_num: Current line number (1-indexed)

    Returns:
        List of ValidationIssue objects
    """
    issues: list[ValidationIssue] = []

    # Parse columns from the line
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return issues

    columns = [c.strip() for c in stripped[1:-1].split("|")]
    col_count = len(columns)

    # Check if this might be a separator row
    is_separator = all(c.replace("-", "").replace(":", "") == "" for c in columns)

    if is_separator:
        # Validate separator format (should be dashes)
        for j, col in enumerate(columns):
            if len(col) < 1:
                issues.append(ValidationIssue(
                    level="error",
                    message=f"Table separator column {j+1} is empty",
                    line=line_num,
                ))
    else:
        # Check for missing separator after header row
        if line_num == 1:
            # First table line is header - check if next line is separator
            if len(all_lines) > 1:
                next_line = all_lines[line_num].strip()  # line_num is 1-indexed, next is index 1
                if next_line.startswith("|") and next_line.endswith("|"):
                    next_cols = [c.strip() for c in next_line[1:-1].split("|")]
                    next_is_separator = all(c.replace("-", "").replace(":", "") == "" for c in next_cols)
                    if not next_is_separator:
                        issues.append(ValidationIssue(
                            level="error",
                            message="Table missing separator row after header",
                            line=line_num,
                        ))

        # Check column consistency with header (assume header is 2 lines above if separator exists)
        if line_num > 2:
            header_line = all_lines[line_num - 3].strip() if line_num > 2 else ""
            sep_line = all_lines[line_num - 2].strip() if line_num > 1 else ""

            if header_line.startswith("|") and header_line.endswith("|"):
                header_cols = [c.strip() for c in header_line[1:-1].split("|")]
                sep_is_valid = False
                if sep_line.startswith("|") and sep_line.endswith("|"):
                    sep_cols = [c.strip() for c in sep_line[1:-1].split("|")]
                    sep_is_valid = all(c.replace("-", "").replace(":", "") == "" for c in sep_cols)

                if sep_is_valid and len(columns) != len(header_cols):
                    issues.append(ValidationIssue(
                        level="error",
                        message=f"Table column mismatch: expected {len(header_cols)} columns, found {col_count}",
                        line=line_num,
                    ))

    return issues
