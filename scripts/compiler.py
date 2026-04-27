"""Knowledge compilation module - transforms raw documents into wiki format.

This module implements the LLM Wiki methodology for knowledge compilation:
- Loads compilation prompts from references/prompts/compile.md
- Calls Anthropic API for structured extraction
- Creates entity and concept pages in wiki/ structure
- Maintains content hashes for change detection

Key functions:
- load_compile_prompt: Read the compilation prompt template
- compile_document: Call LLM to compile raw markdown
- write_entity_page: Create entity page in wiki/entities/
- extract_concepts: Extract concept names from compiled output
- update_index: Update wiki/index.md with knowledge map
"""

import hashlib
import json
import logging
import os
import re
import sqlite3
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

logger = logging.getLogger(__name__)

# Type alias for compiled document structure
class CompiledDocument(BaseModel):
    """Structured output from document compilation."""

    overview: str = ""
    key_content: list[str] = []
    entities: list[dict] = []
    concepts: list[dict] = []
    relations: list[dict] = []
    confidence_annotations: list[str] = []


# Path to prompt template
PROMPT_TEMPLATE_PATH = Path(__file__).parent.parent / "references" / "prompts" / "compile.md"


def load_compile_prompt() -> str:
    """Load the compilation prompt template.

    Returns:
        String content of the prompt template.

    Raises:
        FileNotFoundError: If prompt template file doesn't exist.
    """
    if not PROMPT_TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Prompt template not found at {PROMPT_TEMPLATE_PATH}")

    return PROMPT_TEMPLATE_PATH.read_text(encoding="utf-8")


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of content for change detection.

    Args:
        content: String content to hash.

    Returns:
        Hexadecimal SHA-256 hash string.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def store_content_hash(db_path: Path, file_path: Path, content: str) -> None:
    """Store content hash in SQLite database.

    Args:
        db_path: Path to index.db SQLite file.
        file_path: Path to the raw file.
        content: File content to hash.
    """
    content_hash = compute_content_hash(content)
    file_id = file_path.stem

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Ensure documents table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            path TEXT NOT NULL,
            original_path TEXT,
            format TEXT,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            compiled_at TIMESTAMP,
            status TEXT DEFAULT 'raw',
            hash TEXT
        )
    """)

    # Update or insert hash
    cursor.execute(
        """
        INSERT INTO documents (id, path, hash, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET hash = excluded.hash
        """,
        (file_id, str(file_path), content_hash, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()


def check_hash_changed(db_path: Path, file_path: Path, content: str) -> bool:
    """Check if content hash differs from stored hash.

    Args:
        db_path: Path to index.db SQLite file.
        file_path: Path to the raw file.
        content: Current file content.

    Returns:
        True if content changed (or no stored hash), False otherwise.
    """
    current_hash = compute_content_hash(content)
    file_id = file_path.stem

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("SELECT hash FROM documents WHERE id = ?", (file_id,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return True  # No stored hash, treat as changed

    stored_hash = result[0]
    return current_hash != stored_hash


def get_anthropic_client():
    """Get Anthropic client with API key from environment.

    Returns:
        Anthropic client instance.

    Raises:
        ValueError: If API key not found in environment.
    """
    try:
        import anthropic
    except ImportError:
        raise ImportError("anthropic package not installed. Run: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    return anthropic.Anthropic(api_key=api_key)


def compile_document(
    content: str,
    config,
    force: bool = False,
) -> dict:
    """Compile raw document into structured wiki format using LLM.

    Args:
        content: Raw markdown content to compile.
        config: PMSkillConfig with LLM settings.
        force: Bypass hash check and recompile anyway.

    Returns:
        Dictionary with structured wiki content:
        - overview: str
        - key_content: list[str]
        - entities: list[dict]
        - concepts: list[dict]
        - relations: list[dict]
        - confidence_annotations: list[str]

    Raises:
        ValueError: If API key not configured.
        Exception: If LLM call fails.
    """
    # Load prompt template
    prompt = load_compile_prompt()

    # Get API client
    client = get_anthropic_client()

    # Make API call
    logger.info("Calling Anthropic API for compilation")
    response = client.messages.create(
        model=config.llm.model,
        max_tokens=4096,
        messages=[
            {"role": "user", "content": f"{prompt}\n\n---\n\n## Document to Compile:\n\n{content}"},
        ],
    )

    # Extract text from response
    response_text = ""
    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            response_text += block.text

    # Parse structured content
    compiled = parse_compiled_response(response_text)

    return compiled


def parse_compiled_response(response_text: str) -> dict:
    """Parse LLM response into structured dictionary.

    Args:
        response_text: Raw text from LLM response.

    Returns:
        Structured dictionary with wiki content.
    """
    result = {
        "overview": "",
        "key_content": [],
        "entities": [],
        "concepts": [],
        "relations": [],
        "confidence_annotations": [],
    }

    # Extract overview
    overview_match = re.search(r"## Overview\n(.+?)(?=\n##|\Z)", response_text, re.DOTALL)
    if overview_match:
        result["overview"] = overview_match.group(1).strip()

    # Extract key content
    key_content_match = re.search(r"## Key Content\n(.+?)(?=\n##|\Z)", response_text, re.DOTALL)
    if key_content_match:
        content_lines = key_content_match.group(1).strip().split("\n")
        result["key_content"] = [
            line.strip().lstrip("- ").strip() for line in content_lines if line.strip().startswith("-")
        ]

    # Extract entities
    entities_match = re.search(r"## Entities\n(.+?)(?=\n##|\Z)", response_text, re.DOTALL)
    if entities_match:
        entity_lines = entities_match.group(1).strip().split("\n")
        for line in entity_lines:
            # Parse: - **Entity Name**: Description [CONFIDENCE: LEVEL]
            match = re.match(r"-\s+\*\*(.+?)\*\*:\s*(.+?)(?:\s*\[CONFIDENCE:\s*(\w+)\])?", line)
            if match:
                entity = {
                    "name": match.group(1).strip(),
                    "description": match.group(2).strip(),
                    "confidence": match.group(3) or "UNVERIFIED",
                }
                result["entities"].append(entity)

    # Extract concepts
    concepts_match = re.search(r"## Concepts\n(.+?)(?=\n##|\Z)", response_text, re.DOTALL)
    if concepts_match:
        concept_lines = concepts_match.group(1).strip().split("\n")
        for line in concept_lines:
            match = re.match(r"-\s+\*\*(.+?)\*\*:\s*(.+?)(?:\s*\[CONFIDENCE:\s*(\w+)\])?", line)
            if match:
                concept = {
                    "name": match.group(1).strip(),
                    "description": match.group(2).strip(),
                    "confidence": match.group(3) or "UNVERIFIED",
                }
                result["concepts"].append(concept)

    # Extract relations
    relations_match = re.search(r"## Relations\n(.+?)(?=\n##|\Z)", response_text, re.DOTALL)
    if relations_match:
        relation_lines = relations_match.group(1).strip().split("\n")
        for line in relation_lines:
            # Parse: - Source -- relation --> Target [CONFIDENCE: LEVEL]
            match = re.match(r"-\s*(.+?)\s*--\s*(.+?)\s*-->\s*(.+?)(?:\s*\[CONFIDENCE:\s*(\w+)\])?", line)
            if match:
                relation = {
                    "source": match.group(1).strip(),
                    "relation": match.group(2).strip(),
                    "target": match.group(3).strip(),
                    "confidence": match.group(4) or "UNVERIFIED",
                }
                result["relations"].append(relation)

    # Extract all confidence annotations present
    confidence_levels = re.findall(r"\[CONFIDENCE:\s*(\w+)\]", response_text)
    result["confidence_annotations"] = list(set(confidence_levels))

    return result


def write_entity_page(wiki_dir: Path, name: str, compiled: dict) -> Path:
    """Write entity page to wiki/entities/ directory.

    Args:
        wiki_dir: Path to wiki directory.
        name: Entity name (used as filename).
        compiled: Structured wiki content from compile_document().

    Returns:
        Path to created entity page.
    """
    entities_dir = wiki_dir / "entities"
    entities_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize name for filename
    safe_name = re.sub(r'[<>:"/\\|?*]', "_", name)
    page_path = entities_dir / f"{safe_name}.md"

    # Build page content
    content_lines = [
        f"# {name}",
        "",
        "## Overview",
        compiled.get("overview", ""),
        "",
        "## Key Content",
    ]

    for item in compiled.get("key_content", []):
        content_lines.append(f"- {item}")

    content_lines.extend(["", "## Entities"])
    for entity in compiled.get("entities", []):
        conf = entity.get("confidence", "UNVERIFIED")
        content_lines.append(f"- **{entity['name']}**: {entity['description']} [CONFIDENCE: {conf}]")

    content_lines.extend(["", "## Concepts"])
    for concept in compiled.get("concepts", []):
        conf = concept.get("confidence", "UNVERIFIED")
        content_lines.append(f"- **{concept['name']}**: {concept['description']} [CONFIDENCE: {conf}]")

    content_lines.extend(["", "## Relations"])
    for relation in compiled.get("relations", []):
        conf = relation.get("confidence", "UNVERIFIED")
        content_lines.append(
            f"- {relation['source']} -- {relation['relation']} --> {relation['target']} [CONFIDENCE: {conf}]"
        )

    # Write page
    page_path.write_text("\n".join(content_lines), encoding="utf-8")
    logger.info("Wrote entity page: %s", page_path)

    return page_path


def extract_concepts(compiled: dict) -> list[str]:
    """Extract concept names from compiled output.

    Args:
        compiled: Structured wiki content from compile_document().

    Returns:
        List of concept names.
    """
    concepts = compiled.get("concepts", [])
    return [c.get("name", str(c)) if isinstance(c, dict) else str(c) for c in concepts]


def write_concept_page(wiki_dir: Path, concept: str, sources: list[str]) -> Path:
    """Write concept page to wiki/concepts/ directory.

    Args:
        wiki_dir: Path to wiki directory.
        concept: Concept name.
        sources: List of source entity filenames.

    Returns:
        Path to created concept page.
    """
    concepts_dir = wiki_dir / "concepts"
    concepts_dir.mkdir(parents=True, exist_ok=True)

    # Sanitize name for filename
    safe_name = re.sub(r'[<>:"/\\|?*]', "_", concept)
    page_path = concepts_dir / f"{safe_name}.md"

    # Build page content
    content_lines = [
        f"# {concept}",
        "",
        "## Definition",
        f"This concept is referenced across multiple documents in the knowledge base.",
        "",
        "## Related Sources",
    ]

    for source in sources:
        # Create link to entity page
        source_name = source.replace(".md", "")
        content_lines.append(f"- [[../entities/{source}|{source_name}]]")

    content_lines.extend(["", "## Backlinks", "This concept is mentioned in the following documents:"])

    for source in sources:
        source_name = source.replace(".md", "")
        content_lines.append(f"- [[../entities/{source}|{source_name}]]")

    # Write page
    page_path.write_text("\n".join(content_lines), encoding="utf-8")
    logger.info("Wrote concept page: %s", page_path)

    return page_path


def update_index(wiki_dir: Path, entities: list[str], concepts: list[str]) -> None:
    """Update wiki/index.md with knowledge map.

    Args:
        wiki_dir: Path to wiki directory.
        entities: List of entity names.
        concepts: List of concept names.
    """
    index_path = wiki_dir / "index.md"

    # Build index content
    content_lines = [
        "# Knowledge Base Index",
        "",
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Entities",
        "",
        "Entity pages contain structured information extracted from source documents.",
        "",
    ]

    for entity in entities:
        entity_name = entity.replace(".md", "")
        content_lines.append(f"- [[entities/{entity}|{entity_name}]]")

    content_lines.extend(["", "## Concepts", "", "Concept pages aggregate related information across documents.", ""])

    for concept in concepts:
        concept_name = concept.replace(".md", "")
        content_lines.append(f"- [[concepts/{concept}|{concept_name}]]")

    # Write index
    index_path.write_text("\n".join(content_lines), encoding="utf-8")
    logger.info("Updated wiki index: %s", index_path)


def update_glossary(wiki_dir: Path, terms: dict[str, str]) -> None:
    """Update wiki/glossary.md with term definitions.

    Args:
        wiki_dir: Path to wiki directory.
        terms: Dictionary of term -> definition.
    """
    glossary_path = wiki_dir / "glossary.md"

    # Sort terms alphabetically
    sorted_terms = sorted(terms.items(), key=lambda x: x[0].lower())

    # Build glossary content
    content_lines = [
        "# Glossary",
        "",
        "Terms and definitions extracted from the knowledge base.",
        "",
    ]

    for term, definition in sorted_terms:
        content_lines.append(f"## {term}")
        content_lines.append("")
        content_lines.append(definition)
        content_lines.append("")

    # Write glossary
    glossary_path.write_text("\n".join(content_lines), encoding="utf-8")
    logger.info("Updated glossary: %s", glossary_path)


def write_compile_log(log_dir: Path, summary: dict) -> None:
    """Write compilation log to log/ directory.

    Args:
        log_dir: Path to log directory.
        summary: Dictionary with compilation summary:
            - files_processed: int
            - entities_created: int
            - concepts_extracted: int
            - errors: int
    """
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_path = log_dir / f"compile-{timestamp}.log"

    # Build log content
    content_lines = [
        f"Compilation Log - {datetime.now().isoformat()}",
        "",
        f"Files processed: {summary.get('files_processed', 0)}",
        f"Entities created: {summary.get('entities_created', 0)}",
        f"Concepts extracted: {summary.get('concepts_extracted', 0)}",
        f"Errors: {summary.get('errors', 0)}",
        "",
    ]

    if summary.get("details"):
        content_lines.append("Details:")
        for detail in summary.get("details", []):
            content_lines.append(f"  - {detail}")

    # Write log
    log_path.write_text("\n".join(content_lines), encoding="utf-8")
    logger.info("Wrote compile log: %s", log_path)
