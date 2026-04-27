"""CLI entry point for PM Skill (FND-01)."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import load_config
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


if __name__ == "__main__":
    app()
