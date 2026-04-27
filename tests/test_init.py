"""Tests for directory initialization (FND-03)."""

import pytest
from pathlib import Path


def test_init_creates_directories():
    """Test raw/wiki/log creation."""
    pytest.skip("Wave 0 scaffold")


def test_init_creates_index_db():
    """Test SQLite index creation."""
    pytest.skip("Wave 0 scaffold")


def test_init_idempotent():
    """Running init twice should not error."""
    pytest.skip("Wave 0 scaffold")
