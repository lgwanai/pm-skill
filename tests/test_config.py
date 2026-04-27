"""Tests for TOML configuration (FND-02)."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest


def test_config_defaults():
    """Test default values when no config file exists."""
    from scripts.config import PMSkillConfig

    with patch.dict(os.environ, {}, clear=True):
        config = PMSkillConfig()
        assert config.raw_dir == Path("raw")
        assert config.wiki_dir == Path("wiki")
        assert config.log_dir == Path("log")


def test_config_loads_from_xdg(monkeypatch, tmp_path):
    """Test XDG path loading."""
    from scripts.config import load_config

    xdg_config = tmp_path / ".config" / "pm-skill" / "config.toml"
    xdg_config.parent.mkdir(parents=True)
    xdg_config.write_text('raw_dir = "custom/raw"\n')

    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / ".config"))
    monkeypatch.delenv("HOME", raising=False)

    config = load_config()
    assert str(config.raw_dir) == "custom/raw"


def test_config_local_fallback(tmp_path, monkeypatch):
    """Test .pm-skill.toml loading."""
    from scripts.config import load_config

    local_config = tmp_path / ".pm-skill.toml"
    local_config.write_text('raw_dir = "local/raw"\n')

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("HOME", raising=False)

    config = load_config()
    assert str(config.raw_dir) == "local/raw"


def test_config_raw_dir_path():
    """Test raw_dir configuration."""
    from scripts.config import PMSkillConfig

    config = PMSkillConfig(raw_dir=Path("custom/raw"))
    assert config.raw_dir == Path("custom/raw")


def test_config_llm_settings():
    """Test LLM configuration."""
    from scripts.config import LLMConfig, PMSkillConfig

    llm = LLMConfig(model="claude-sonnet-4-6-20250528", api_key_env="MY_API_KEY")
    config = PMSkillConfig(llm=llm)
    assert config.llm.model == "claude-sonnet-4-6-20250528"
    assert config.llm.api_key_env == "MY_API_KEY"