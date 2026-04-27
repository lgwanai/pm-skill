"""CLI entry point for PM Skill (FND-01, FND-02, FND-03, IMP-01 to IMP-06, CMP-01 to CMP-08, RET-04)."""

import logging
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .config import load_config
from .importer import import_batch, import_document
from .utils.init import init_knowledge_base

logger = logging.getLogger(__name__)

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


@app.command()
def compile(
    file: Path = typer.Option(None, "--file", "-f", help="Compile single file"),
    force: bool = typer.Option(False, "--force", help="Force recompilation"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be compiled"),
    model: str = typer.Option(None, "--model", "-m", help="Override LLM model"),
) -> None:
    """Compile raw documents into wiki knowledge base.

    Transforms raw Markdown files in raw/ directory into structured wiki pages
    in wiki/entities/ with confidence annotations using LLM-powered compilation.

    Each raw file generates an entity page with:
    - Overview, Key Content, Entities, Concepts, Relations sections
    - Confidence annotations (EXTRACTED/INFERRED/AMBIGUOUS/UNVERIFIED)
    - FTS5 search index entry
    """
    from .compiler import (
        check_hash_changed,
        compile_document,
        extract_concepts,
        store_content_hash,
        update_index,
        write_compile_log,
        write_concept_page,
        write_entity_page,
    )
    from .search import init_fts5_table, index_wiki_page

    cfg = load_config()

    # Override model if specified
    if model:
        from .config import LLMConfig

        cfg.llm = LLMConfig(model=model, api_key_env=cfg.llm.api_key_env)

    # Ensure directories exist
    cfg.raw_dir.mkdir(parents=True, exist_ok=True)
    cfg.wiki_dir.mkdir(parents=True, exist_ok=True)
    cfg.log_dir.mkdir(parents=True, exist_ok=True)

    # Initialize FTS5 table
    db_path = cfg.wiki_dir.parent / "index.db"
    init_fts5_table(db_path)

    # Get files to compile
    if file:
        files_to_compile = [file]
    else:
        files_to_compile = list(cfg.raw_dir.glob("*.md"))

    if not files_to_compile:
        console.print("[yellow]No files to compile[/yellow]")
        return

    if dry_run:
        console.print("[blue]Files to compile:[/blue]")
        for f in files_to_compile:
            console.print(f"  {f.name}")
        return

    # Track results
    entities_created: list[str] = []
    all_concepts: dict[str, list[str]] = {}  # concept -> sources
    files_processed = 0
    errors = 0
    details: list[str] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Compiling documents...", total=len(files_to_compile))

        for raw_file in files_to_compile:
            progress.update(task, description=f"Compiling {raw_file.name}")

            try:
                content = raw_file.read_text(encoding="utf-8")

                # Check if changed (skip if hash matches unless forced)
                if not force and not check_hash_changed(db_path, raw_file, content):
                    logger.info("Skipping unchanged file: %s", raw_file.name)
                    details.append(f"Skipped {raw_file.name} (unchanged)")
                    progress.advance(task)
                    continue

                # Compile document
                compiled = compile_document(content, cfg, force=force)

                # Write entity page
                entity_name = raw_file.stem
                entity_path = write_entity_page(cfg.wiki_dir, entity_name, compiled)
                entities_created.append(entity_name)

                # Index in FTS5
                page_content = entity_path.read_text(encoding="utf-8")
                index_wiki_page(
                    db_path=db_path,
                    path=str(entity_path.relative_to(cfg.wiki_dir.parent)),
                    title=entity_name,
                    content=page_content,
                    page_type="entity",
                )

                # Track concepts
                concepts = extract_concepts(compiled)
                for concept in concepts:
                    if concept not in all_concepts:
                        all_concepts[concept] = []
                    all_concepts[concept].append(f"{entity_name}.md")

                # Store hash for future checks
                store_content_hash(db_path, raw_file, content)

                files_processed += 1
                details.append(f"Compiled {raw_file.name} -> {entity_path.name}")

            except Exception as e:
                errors += 1
                logger.error("Failed to compile %s: %s", raw_file.name, e)
                details.append(f"ERROR: {raw_file.name} - {e}")

            progress.advance(task)

    # Write concept pages
    concept_names: list[str] = []
    for concept, sources in all_concepts.items():
        concept_path = write_concept_page(cfg.wiki_dir, concept, sources)
        concept_names.append(concept)

        # Index concept page
        page_content = concept_path.read_text(encoding="utf-8")
        index_wiki_page(
            db_path=db_path,
            path=str(concept_path.relative_to(cfg.wiki_dir.parent)),
            title=concept,
            content=page_content,
            page_type="concept",
        )

    # Update wiki index
    update_index(cfg.wiki_dir, entities_created, concept_names)

    # Write compile log
    write_compile_log(
        cfg.log_dir,
        {
            "files_processed": files_processed,
            "entities_created": len(entities_created),
            "concepts_extracted": len(concept_names),
            "errors": errors,
            "details": details,
        },
    )

    # Show summary
    console.print("[green]Compilation complete[/green]")
    console.print(f"  Files processed: {files_processed}")
    console.print(f"  Entities created: {len(entities_created)}")
    console.print(f"  Concepts extracted: {len(concept_names)}")
    if errors:
        console.print(f"[red]  Errors: {errors}[/red]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query string"),
    context: int = typer.Option(3, "--context", "-c", help="Number of context lines to show"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, json, table"),
    scope: str = typer.Option("all", "--scope", "-s", help="Search scope: entity, concept, all"),
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum number of results"),
) -> None:
    """Search the wiki knowledge base for matching pages.

    Uses FTS5 full-text search with BM25 ranking to find relevant wiki pages.
    Results include file path, title, and matching context.

    Examples:
        pm-skill search authentication
        pm-skill search "password hashing" --scope entity
        pm-skill search security --format json
    """
    from .search import format_search_results, search_wiki

    cfg = load_config()
    db_path = cfg.wiki_dir.parent / "index.db"

    if not db_path.exists():
        console.print("[yellow]No search index found. Run 'compile' first.[/yellow]")
        raise typer.Exit(1)

    try:
        results = search_wiki(db_path, query, scope=scope, limit=limit)

        if not results:
            console.print(f"[yellow]No results found for:[/yellow] {query}")
            return

        formatted = format_search_results(results, context_lines=context, format_type=format)
        console.print(formatted)

    except Exception as e:
        console.print(f"[red]Search error:[/red] {e}")
        raise typer.Exit(1)


@app.command("list")
def list_pages(
    scope: str = typer.Option("all", "--scope", "-s", help="List scope: entity, concept, all"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, json, table"),
) -> None:
    """List all wiki pages in the knowledge base.

    Shows all entity and concept pages with their titles.
    Titles are extracted from frontmatter or first heading.

    Examples:
        pm-skill list
        pm-skill list --scope entity
        pm-skill list --format json
    """
    from .search import format_search_results, list_wiki_pages

    cfg = load_config()
    wiki_dir = cfg.wiki_dir

    if not wiki_dir.exists():
        console.print("[yellow]Wiki directory not found. Run 'compile' first.[/yellow]")
        raise typer.Exit(1)

    try:
        results = list_wiki_pages(wiki_dir, scope=scope)

        if not results:
            console.print(f"[yellow]No pages found in scope:[/yellow] {scope}")
            return

        formatted = format_search_results(results, context_lines=0, format_type=format)
        console.print(formatted)

    except Exception as e:
        console.print(f"[red]List error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()