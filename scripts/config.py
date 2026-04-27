"""Configuration management with TOML support (FND-02)."""

import os
import sys
from pathlib import Path

from pydantic import BaseModel

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class LLMConfig(BaseModel):
    """LLM configuration settings."""

    model: str = "claude-sonnet-4-6-20250528"
    api_key_env: str = "ANTHROPIC_API_KEY"


class PMSkillConfig(BaseModel):
    """PM Skill configuration."""

    raw_dir: Path = Path("raw")
    wiki_dir: Path = Path("wiki")
    log_dir: Path = Path("log")
    llm: LLMConfig = LLMConfig()


def _get_xdg_config_path() -> Path | None:
    """Get XDG config path following XDG Base Directory spec."""
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home) / "pm-skill" / "config.toml"

    home = os.environ.get("HOME")
    if home:
        return Path(home) / ".config" / "pm-skill" / "config.toml"

    return None


def _get_local_config_path() -> Path:
    """Get local config path (current directory)."""
    return Path.cwd() / ".pm-skill.toml"


def _load_toml_file(path: Path) -> dict:
    """Load and parse a TOML file."""
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_config() -> PMSkillConfig:
    """Load configuration from XDG path or local fallback."""
    config_data: dict = {}

    # Try XDG path first
    xdg_path = _get_xdg_config_path()
    if xdg_path and xdg_path.exists():
        config_data = _load_toml_file(xdg_path)
    else:
        # Fall back to local config
        local_path = _get_local_config_path()
        if local_path.exists():
            config_data = _load_toml_file(local_path)

    # Build config from loaded data
    if not config_data:
        return PMSkillConfig()

    # Handle nested llm config
    llm_data = config_data.pop("llm", None)
    llm_config = LLMConfig(**llm_data) if llm_data else LLMConfig()

    # Convert string paths to Path objects
    for key in ("raw_dir", "wiki_dir", "log_dir"):
        if key in config_data:
            config_data[key] = Path(config_data[key])

    return PMSkillConfig(llm=llm_config, **config_data)