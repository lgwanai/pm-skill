"""Document import logic using markitdown (IMP-01 to IMP-06)."""

import logging
from pathlib import Path

from markitdown import MarkItDown

from .utils.validation import validate_markdown

logger = logging.getLogger(__name__)

# Supported formats and their extensions
SUPPORTED_FORMATS = {
    "pdf": [".pdf"],
    "docx": [".doc", ".docx"],
    "html": [".html", ".htm"],
}


def _detect_format(source_path: Path) -> str | None:
    """Detect document format from file extension.

    Args:
        source_path: Path to source document

    Returns:
        Format string ("pdf", "docx", "html") or None if unsupported
    """
    ext = source_path.suffix.lower()
    for fmt, extensions in SUPPORTED_FORMATS.items():
        if ext in extensions:
            return fmt
    return None


def import_document(
    source_path: Path,
    output_dir: Path,
    format: str | None = None,
    no_validate: bool = False,
) -> Path:
    """Import a document and convert to Markdown.

    Uses markitdown library for PDF, DOCX, and HTML conversion.

    Args:
        source_path: Path to source document (PDF, DOCX, HTML)
        output_dir: Directory to save converted Markdown
        format: Optional format override ("pdf", "docx", "html")
        no_validate: Skip validation if True

    Returns:
        Path to created Markdown file

    Raises:
        ValueError: If format is unsupported
    """
    source_path = Path(source_path)
    output_dir = Path(output_dir)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Detect or use provided format
    detected_format = format or _detect_format(source_path)
    if not detected_format:
        raise ValueError(f"Unsupported document format: {source_path.suffix}")

    # Convert using markitdown
    md = MarkItDown()
    result = md.convert(str(source_path))
    markdown_content = result.text_content

    # Determine output path
    output_path = output_dir / f"{source_path.stem}.md"

    # Validate unless skipped
    if not no_validate:
        issues = validate_markdown(markdown_content)
        for issue in issues:
            if issue.level == "error":
                logger.warning(
                    "Validation issue at line %d: %s",
                    issue.line,
                    issue.message,
                )
            elif issue.level == "warn":
                logger.info(
                    "Validation warning at line %d: %s",
                    issue.line,
                    issue.message,
                )

    # Save with UTF-8 encoding
    output_path.write_text(markdown_content, encoding="utf-8")
    logger.info("Saved Markdown to %s", output_path)

    return output_path


def import_batch(
    paths: list[Path],
    output_dir: Path,
    no_validate: bool = False,
    quiet: bool = False,
    log_dir: Path | None = None,
) -> tuple[int, int]:
    """Import multiple documents in batch.

    Args:
        paths: List of document paths to import
        output_dir: Directory to save converted Markdown files
        no_validate: Skip validation if True
        quiet: Suppress progress output
        log_dir: Optional directory for failure logs

    Returns:
        Tuple of (success_count, failure_count)
    """
    from datetime import datetime
    import sys

    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn

    console = Console(file=sys.stderr) if quiet else Console()
    output_dir = Path(output_dir)

    success_count = 0
    failure_count = 0
    failures: list[tuple[Path, str]] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        disable=quiet,
    ) as progress:
        task = progress.add_task("Importing documents...", total=len(paths))

        for path in paths:
            path = Path(path)
            progress.update(task, description=f"Importing {path.name}")

            try:
                import_document(path, output_dir, no_validate=no_validate)
                success_count += 1
            except Exception as e:
                failure_count += 1
                failures.append((path, str(e)))
                logger.error("Failed to import %s: %s", path, e)

            progress.advance(task)

    # Log failures if log_dir provided
    if log_dir and failures:
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = log_dir / f"import-{timestamp}.log"

        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Import Log - {datetime.now().isoformat()}\n")
            f.write(f"Success: {success_count}, Failures: {failure_count}\n\n")
            for failed_path, error in failures:
                f.write(f"FAILED: {failed_path}\n  Error: {error}\n")

        console.print(f"[yellow]Log saved to {log_file}[/yellow]")

    return (success_count, failure_count)
