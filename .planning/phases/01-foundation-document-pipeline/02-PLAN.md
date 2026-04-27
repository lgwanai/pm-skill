---
phase: 01-foundation-document-pipeline
plan: 02
type: tdd
wave: 1
depends_on: ["01"]
files_modified:
  - SKILL.md
  - scripts/__init__.py
  - scripts/cli.py
  - scripts/config.py
  - scripts/utils/__init__.py
  - scripts/utils/init.py
autonomous: true
requirements:
  - FND-01
  - FND-02
  - FND-03

must_haves:
  truths:
    - "User can run pm-skill --help and see available commands"
    - "User can run pm-skill init and see directories created"
    - "User can run pm-skill config and see current settings"
    - "SKILL.md exists with proper frontmatter"
  artifacts:
    - path: "SKILL.md"
      provides: "Skill definition for Claude Code"
      contains: "name: pm-skill"
      min_lines: 20
    - path: "scripts/cli.py"
      provides: "CLI entry point with Typer"
      exports: ["app", "init", "config"]
    - path: "scripts/config.py"
      provides: "Configuration management with TOML"
      exports: ["PMSkillConfig", "load_config"]
    - path: "scripts/utils/init.py"
      provides: "Directory initialization logic"
      exports: ["init_knowledge_base"]
  key_links:
    - from: "scripts/cli.py"
      to: "scripts/config.py"
      via: "from .config import load_config"
      pattern: "from.*config import"
    - from: "scripts/cli.py"
      to: "scripts/utils/init.py"
      via: "from .utils.init import init_knowledge_base"
      pattern: "from.*init import"
    - from: "scripts/config.py"
      to: "~/.config/pm-skill/config.toml"
      via: "XDG Base Directory spec"
      pattern: "\.config/pm-skill"
    - from: "pyproject.toml [project.scripts]"
      to: "scripts.cli:app"
      via: "entry point wiring"
      pattern: "pm-skill = \"scripts.cli:app\""
---

<objective>
Create the PM Skill foundation including SKILL.md with frontmatter, CLI structure using Typer, directory initialization logic, and configuration management with TOML support. This establishes the core skill architecture that document import will build upon.

Purpose: Establish working skill infrastructure that Claude Code can discover and users can interact with.
Output: Functional CLI with init and config commands, proper skill definition.
</objective>

<execution_context>
@/Users/wuliang/.claude/get-shit-done/workflows/execute-plan.md
@/Users/wuliang/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01-foundation-document-pipeline/01-CONTEXT.md
@.planning/phases/01-foundation-document-pipeline/01-RESEARCH.md
@.planning/phases/01-foundation-document-pipeline/01-PLAN.md
</context>

<interfaces>
<!-- Key interfaces from RESEARCH.md code examples -->

SKILL.md frontmatter pattern:
```markdown
---
name: pm-skill
description: Product Manager Knowledge Assistant. Import PM documents (PDF/DOC/HTML), compile them into a searchable knowledge base, and generate PRD documents. Use this skill when users want to manage product documentation or create PRDs.
---

# PM Skill

## Commands

### init
Initialize the knowledge base directory structure.

### config
View or set configuration values.
```

Typer CLI pattern:
```python
import typer
from rich.console import Console

app = typer.Typer(name="pm-skill", help="PM Skill - Product Manager Knowledge Assistant")
console = Console()

@app.command()
def init(...): ...

@app.command()
def config(...): ...
```

pydantic-settings pattern:
```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class PMSkillConfig(BaseSettings):
    raw_dir: Path = Path("raw")
    wiki_dir: Path = Path("wiki")
    log_dir: Path = Path("log")
```
</interfaces>

<tasks>

<task type="auto" tdd="true">
  <name>Task 1: Create SKILL.md with frontmatter</name>
  <files>SKILL.md</files>
  <behavior>
    - Test 1: SKILL.md file exists at project root
    - Test 2: SKILL.md contains frontmatter with name field
    - Test 3: SKILL.md contains frontmatter with description field
    - Test 4: SKILL.md describes available commands (init, config, import)
  </behavior>
  <action>
Write tests first in tests/test_skill.py (replace skip stubs):
```python
def test_skill_md_exists():
    assert Path("SKILL.md").exists()

def test_skill_md_frontmatter_name():
    content = Path("SKILL.md").read_text()
    assert "name: pm-skill" in content

def test_skill_md_frontmatter_description():
    content = Path("SKILL.md").read_text()
    assert "description:" in content
```

Create SKILL.md with proper frontmatter:
- name: pm-skill
- description: Product Manager Knowledge Assistant (from CONTEXT.md locked decision)
- Document commands: init, config, import
- Document directory structure: raw/, wiki/, log/
- Document configuration location: ~/.config/pm-skill/config.toml

Run tests: pytest tests/test_skill.py -v
  </action>
  <verify>
    <automated>pytest tests/test_skill.py -v</automated>
  </verify>
  <done>SKILL.md exists with valid frontmatter, all skill tests pass</done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Create configuration system with TOML support</name>
  <files>scripts/__init__.py, scripts/config.py</files>
  <behavior>
    - Test 1: load_config() returns default PMSkillConfig
    - Test 2: PMSkillConfig has raw_dir, wiki_dir, log_dir attributes
    - Test 3: load_config() reads from XDG path if exists
    - Test 4: load_config() reads from .pm-skill.toml if exists
    - Test 5: Configuration values override defaults
  </behavior>
  <action>
Write tests first in tests/test_config.py:
```python
from pathlib import Path
from scripts.config import PMSkillConfig, load_config

def test_config_defaults():
    config = PMSkillConfig()
    assert config.raw_dir == Path("raw")
    assert config.wiki_dir == Path("wiki")
    assert config.log_dir == Path("log")

def test_config_loads_from_xdg(monkeypatch, tmp_path):
    xdg_config = tmp_path / ".config" / "pm-skill" / "config.toml"
    xdg_config.parent.mkdir(parents=True)
    xdg_config.write_text('raw_dir = "custom/raw"')
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    config = load_config()
    assert str(config.raw_dir) == "custom/raw"

def test_config_local_fallback(tmp_path, monkeypatch):
    local_config = tmp_path / ".pm-skill.toml"
    local_config.write_text('raw_dir = "local/raw"')
    monkeypatch.chdir(tmp_path)
    config = load_config()
    assert str(config.raw_dir) == "local/raw"
```

Create scripts/config.py:
- PMSkillConfig class with pydantic-settings
- raw_dir, wiki_dir, log_dir: Path fields with defaults
- llm: LLMConfig nested model (model, api_key_env)
- load_config() function following XDG spec:
  1. Check ~/.config/pm-skill/config.toml
  2. Check ./.pm-skill.toml
  3. Return defaults if neither exists
- Use tomllib for TOML parsing (Python 3.11+ stdlib)

Create scripts/__init__.py (empty or with version).

Run tests: pytest tests/test_config.py -v
  </action>
  <verify>
    <automated>pytest tests/test_config.py -v</automated>
  </verify>
  <done>Configuration system works with TOML files and XDG spec, all config tests pass</done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Create directory initialization logic</name>
  <files>scripts/utils/__init__.py, scripts/utils/init.py</files>
  <behavior>
    - Test 1: init_knowledge_base() creates raw/, wiki/, log/ directories
    - Test 2: init_knowledge_base() creates index.db SQLite file
    - Test 3: Running init twice does not error (idempotent)
    - Test 4: Directories are created with correct permissions
  </behavior>
  <action>
Write tests first in tests/test_init.py:
```python
from pathlib import Path
from scripts.utils.init import init_knowledge_base

def test_init_creates_directories(tmp_path):
    init_knowledge_base(tmp_path)
    assert (tmp_path / "raw").is_dir()
    assert (tmp_path / "wiki").is_dir()
    assert (tmp_path / "log").is_dir()

def test_init_creates_index_db(tmp_path):
    init_knowledge_base(tmp_path)
    db_path = tmp_path / "index.db"
    assert db_path.exists()
    # Verify it's a valid SQLite database
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    conn.execute("SELECT 1")
    conn.close()

def test_init_idempotent(tmp_path):
    init_knowledge_base(tmp_path)
    init_knowledge_base(tmp_path)  # Should not raise
    assert (tmp_path / "raw").exists()
```

Create scripts/utils/init.py:
- init_knowledge_base(base_path: Path) function
- Creates directories: raw/, wiki/, log/
- Creates index.db with basic schema:
  - documents table (id, path, hash, created_at)
  - Prepare FTS5 virtual table for Phase 2
- Use Path.mkdir(parents=True, exist_ok=True)
- Use sqlite3 for database creation

Create scripts/utils/__init__.py (empty).

Run tests: pytest tests/test_init.py -v
  </action>
  <verify>
    <automated>pytest tests/test_init.py -v</automated>
  </verify>
  <done>init_knowledge_base creates correct structure, all init tests pass</done>
</task>

<task type="auto" tdd="true">
  <name>Task 4: Create CLI entry point with Typer</name>
  <files>scripts/cli.py</files>
  <behavior>
    - Test 1: pm-skill --help shows init, config, import commands
    - Test 2: pm-skill init creates directory structure
    - Test 3: pm-skill config shows current configuration
    - Test 4: pm-skill config key shows specific value
    - Test 5: CLI uses Rich for colored output
  </behavior>
  <action>
Write tests first in tests/test_cli.py (already created in Plan 01 Task 3, replace skip stubs):
```python
from typer.testing import CliRunner
from scripts.cli import app

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "config" in result.output

def test_cli_init(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert (tmp_path / "knowledge-base" / "raw").exists()

def test_cli_config_show():
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "raw_dir" in result.output
```

Create scripts/cli.py:
- Typer app with name "pm-skill"
- init command: calls init_knowledge_base, prints success with Rich
- config command: shows current config values
- Use Rich Console for colored output
- Entry point: if __name__ == "__main__": app()

CRITICAL - CLI entry point wiring:
The entry point was already defined in pyproject.toml (Plan 01 Task 1) as:
```toml
[project.scripts]
pm-skill = "scripts.cli:app"
```

This wiring creates the `pm-skill` command that calls `app` from `scripts.cli`. Verify the entry point is functional by running `pm-skill --help` after this task completes. The app object in scripts/cli.py MUST be a Typer instance (or callable) for the entry point to work.

Run tests: pytest tests/test_cli.py -v
  </action>
  <verify>
    <automated>pytest tests/test_cli.py -v && pm-skill --help</automated>
  </verify>
  <done>CLI works with init and config commands, all CLI tests pass</done>
</task>

</tasks>

<verification>
Run all foundation tests:
```bash
pytest tests/test_skill.py tests/test_config.py tests/test_init.py -v
```

Manual verification:
```bash
pm-skill --help          # Should show init, config, import commands
pm-skill init            # Should create knowledge-base/ structure
pm-skill config          # Should show current configuration
```
</verification>

<success_criteria>
- SKILL.md exists with proper frontmatter (name, description)
- Configuration system loads from XDG path and local fallback
- init command creates raw/, wiki/, log/, index.db
- config command displays current settings
- All tests in test_skill.py, test_config.py, test_init.py pass
- CLI entry point works: pm-skill --help
</success_criteria>

<output>
After completion, create `.planning/phases/01-foundation-document-pipeline/02-SUMMARY.md`
</output>