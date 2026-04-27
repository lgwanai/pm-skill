"""CLI entry point for PM Skill (FND-01, FND-02, FND-03, IMP-01 to IMP-06)."""

from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import load_config
from .importer import import_batch, import_document
from .utils.init import init_knowledge_base

app = typer.Typer(
    name="pm-skill",
    help="PM Skill - Product Manager Knowledge Assistant",
)
console = Console()


@app.command()
def init(
    path: Path = typer.Option(
        Path("knowledge-base"),
        "--path",
        "-p",
        help="Path for knowledge base directory",
    ),
) -> None:
    """Initialize the knowledge base directory structure."""
    console.print(f"[blue]Initializing knowledge base at[/blue] {path}")
    init_knowledge_base(path)
    console.print("[green]Created:[/green]")
    console.print(f"  {path / 'raw'} - Imported Markdown files")
    console.print(f"  {path / 'wiki'} - Compiled knowledge (Phase 2)")
    console.print(f"  {path / 'log'} - Processing logs")
    console.print(f"  {path / 'index.db'} - SQLite metadata")


@app.command()
def config(
    key: str = typer.Argument(None, help="Specific config key to display"),
) -> None:
    """View current configuration values."""
    cfg = load_config()

    if key:
        # Display specific key
        value = getattr(cfg, key, None) or getattr(cfg.llm, key, None)
        if value is None:
            console.print(f"[red]Unknown config key: {key}[/red]")
            raise typer.Exit(1)
        console.print(f"{key}: {value}")
    else:
        # Display all config in a table
        table = Table(title="PM Skill Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("raw_dir", str(cfg.raw_dir))
        table.add_row("wiki_dir", str(cfg.wiki_dir))
        table.add_row("log_dir", str(cfg.log_dir))
        table.add_row("llm.model", cfg.llm.model)
        table.add_row("llm.api_key_env", cfg.llm.api_key_env)

        console.print(table)


@app.command("import")
def import_doc(
    path: Path = typer.Argument(..., exists=True, help="Document path to import"),
    format: str = typer.Option(None, "--format", "-f", help="Force format (pdf, docx, html)"),
    no_validate: bool = typer.Option(False, "--no-validate", help="Skip validation checks"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output"),
) -> None:
    """Import a document into the knowledge base.

    Converts PDF, DOCX, and HTML files to Markdown and stores in raw/ directory.
    """
    cfg = load_config()

    # Ensure raw directory exists
    cfg.raw_dir.mkdir(parents=True, exist_ok=True)

    if not quiet:
        console.print(f"[blue]Importing[/blue] {path.name}...")

    try:
        output = import_document(
            source_path=path,
            output_dir=cfg.raw_dir,
            format=format,
            no_validate=no_validate,
        )

        if not quiet:
            console.print(f"[green]Created:[/green] {output}")

            # Show validation summary if enabled
            if not no_validate:
                content = output.read_text(encoding="utf-8")
                from .utils.validation import validate_markdown

                issues = validate_markdown(content)
                if issues:
                    errors = [i for i in issues if i.level == "error"]
                    warns = [i for i in issues if i.level == "warn"]
                    infos = [i for i in issues if i.level == "info"]

                    if errors:
                        console.print(f"[red]Errors: {len(errors)}[/red]")
                    if warns:
                        console.print(f"[yellow]Warnings: {len(warns)}[/yellow]")
                    if infos:
                        console.print(f"[blue]Info: {len(infos)}[/blue]")
                else:
                    console.print("[green]Validation: OK[/green]")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Import failed:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()