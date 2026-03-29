import os
import tempfile
from pathlib import Path

import pytest
from click.testing import CliRunner

from clir.cli import init, ls, new, settings
from clir.utils.config import configure_active_db, read_setting, write_setting
from clir.utils.db import find_local_db, get_active_db_path, set_active_db


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset db_file and default_current_folder before every test."""
    set_active_db(None)
    write_setting("default_current_folder", False)
    yield
    set_active_db(None)
    write_setting("default_current_folder", False)


# --- helpers ---

def _make_project_dir():
    return tempfile.mkdtemp(prefix="clir-local-test-")


# --- clir init ---

def test_init_creates_local_db():
    project_dir = _make_project_dir()
    original_dir = os.getcwd()
    os.chdir(project_dir)
    try:
        runner = CliRunner()
        result = runner.invoke(init)
        assert result.exit_code == 0, result.output
        assert (Path(project_dir) / ".clir" / "clir.db").exists()
        assert "initialized" in result.output
    finally:
        os.chdir(original_dir)


def test_init_already_initialized_is_idempotent():
    project_dir = _make_project_dir()
    original_dir = os.getcwd()
    os.chdir(project_dir)
    try:
        runner = CliRunner()
        runner.invoke(init)
        result = runner.invoke(init)
        assert result.exit_code == 0, result.output
        assert "already initialized" in result.output
    finally:
        os.chdir(original_dir)


# --- find_local_db ---

def test_find_local_db_returns_path_when_present():
    project_dir = _make_project_dir()
    original_dir = os.getcwd()
    os.chdir(project_dir)
    try:
        runner = CliRunner()
        runner.invoke(init)
        db_path = find_local_db()
        assert db_path is not None
        assert db_path == Path(project_dir) / ".clir" / "clir.db"
    finally:
        os.chdir(original_dir)


def test_find_local_db_returns_none_when_absent():
    project_dir = _make_project_dir()
    original_dir = os.getcwd()
    os.chdir(project_dir)
    try:
        assert find_local_db() is None
    finally:
        os.chdir(original_dir)


# --- -l / --local flag ---

def test_local_flag_errors_without_init():
    project_dir = _make_project_dir()
    original_dir = os.getcwd()
    os.chdir(project_dir)
    try:
        runner = CliRunner()
        result = runner.invoke(ls, ['-l'])
        assert result.exit_code != 0
        assert "clir init" in result.output
    finally:
        os.chdir(original_dir)


def test_local_flag_uses_local_db():
    project_dir = _make_project_dir()
    original_dir = os.getcwd()
    os.chdir(project_dir)
    try:
        runner = CliRunner()
        runner.invoke(init)
        result = runner.invoke(new, ['-c', 'local-cmd', '-d', 'local desc', '-t', 'local-tag', '-l'])
        assert result.exit_code == 0, result.output
        assert "[local:" in result.output

        ls_result = runner.invoke(ls, ['-l'])
        assert ls_result.exit_code == 0, ls_result.output
        assert "local-cmd" in ls_result.output
    finally:
        os.chdir(original_dir)


def test_global_flag_uses_global_db():
    """Commands saved with -l should not appear when using -G."""
    project_dir = _make_project_dir()
    original_dir = os.getcwd()
    os.chdir(project_dir)
    try:
        runner = CliRunner()
        runner.invoke(init)
        runner.invoke(new, ['-c', 'local-only-cmd', '-d', 'desc', '-t', 'test', '-l'])

        ls_result = runner.invoke(ls, ['-G'])
        assert ls_result.exit_code == 0, ls_result.output
        assert "local-only-cmd" not in ls_result.output
    finally:
        os.chdir(original_dir)


# --- configure_active_db ---

def test_configure_active_db_resets_to_global():
    set_active_db(Path("/some/fake/path"))
    configure_active_db(local=False, use_global=False)
    assert get_active_db_path() == Path.home() / ".clir" / "clir.db"


def test_configure_active_db_use_global_ignores_local():
    project_dir = _make_project_dir()
    original_dir = os.getcwd()
    os.chdir(project_dir)
    try:
        runner = CliRunner()
        runner.invoke(init)
        configure_active_db(local=False, use_global=True)
        assert get_active_db_path() == Path.home() / ".clir" / "clir.db"
    finally:
        os.chdir(original_dir)


# --- settings ---

def test_settings_read_write():
    write_setting("default_current_folder", True)
    assert read_setting("default_current_folder") is True
    write_setting("default_current_folder", False)
    assert read_setting("default_current_folder") is False


def test_settings_command_shows_active_db():
    runner = CliRunner()
    result = runner.invoke(settings)
    assert result.exit_code == 0, result.output
    assert "clir.db" in result.output


def test_settings_command_enables_default_local():
    runner = CliRunner()
    result = runner.invoke(settings, ['--default-local'])
    assert result.exit_code == 0, result.output
    assert read_setting("default_current_folder") is True


def test_settings_command_disables_default_local():
    write_setting("default_current_folder", True)
    runner = CliRunner()
    result = runner.invoke(settings, ['--no-default-local'])
    assert result.exit_code == 0, result.output
    assert read_setting("default_current_folder") is False


# --- default_current_folder auto-detection ---

def test_auto_local_when_default_current_folder_enabled():
    project_dir = _make_project_dir()
    original_dir = os.getcwd()
    os.chdir(project_dir)
    try:
        runner = CliRunner()
        runner.invoke(init)
        write_setting("default_current_folder", True)

        configure_active_db()
        assert get_active_db_path() == Path(project_dir) / ".clir" / "clir.db"
    finally:
        os.chdir(original_dir)


def test_no_auto_local_when_default_current_folder_disabled():
    project_dir = _make_project_dir()
    original_dir = os.getcwd()
    os.chdir(project_dir)
    try:
        runner = CliRunner()
        runner.invoke(init)
        write_setting("default_current_folder", False)

        configure_active_db()
        assert get_active_db_path() == Path.home() / ".clir" / "clir.db"
    finally:
        os.chdir(original_dir)
