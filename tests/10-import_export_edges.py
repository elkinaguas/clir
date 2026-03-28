import json
import builtins

import pytest

from clir.command import CommandTable
import clir.command as command_module


def test_import_commands_raises_for_missing_file():
    table = object.__new__(CommandTable)
    table.commands = {}

    with pytest.raises(FileNotFoundError):
        table.import_commands("does-not-exist.json")


def test_import_commands_raises_for_invalid_json(tmp_path):
    table = object.__new__(CommandTable)
    table.commands = {}

    invalid_file = tmp_path / "broken.json"
    invalid_file.write_text("{ not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="An error occurred while reading the file"):
        table.import_commands(str(invalid_file))


def test_import_commands_raises_for_non_object_payload(tmp_path):
    table = object.__new__(CommandTable)
    table.commands = {}

    invalid_file = tmp_path / "broken.json"
    invalid_file.write_text(json.dumps(["echo hi"]), encoding="utf-8")

    with pytest.raises(ValueError, match="Import payload must be a JSON object"):
        table.import_commands(str(invalid_file))


def test_import_commands_raises_for_missing_required_keys(tmp_path):
    table = object.__new__(CommandTable)
    table.commands = {}

    invalid_file = tmp_path / "broken.json"
    invalid_file.write_text(
        json.dumps({"echo hi": {"description": "desc", "tag": "ops"}}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match=r"missing required key\(s\): creation_date, last_modif_date"):
        table.import_commands(str(invalid_file))


def test_import_commands_raises_for_non_object_command_metadata(tmp_path):
    table = object.__new__(CommandTable)
    table.commands = {}

    invalid_file = tmp_path / "broken.json"
    invalid_file.write_text(json.dumps({"echo hi": "desc"}), encoding="utf-8")

    with pytest.raises(ValueError, match="Import payload for command 'echo hi' must be an object"):
        table.import_commands(str(invalid_file))


def test_import_existing_command_with_no_changes_skips_write(tmp_path, monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {
        "echo hi": {
            "description": "desc",
            "tag": "tag",
            "creation_date": "2023-01-01 00:00:00.000",
            "last_modif_date": "2023-01-01 00:00:00.000",
        }
    }

    import_file = tmp_path / "import.json"
    import_file.write_text(
        json.dumps(
            {
                "echo hi": {
                    "description": "desc",
                    "tag": "tag",
                    "creation_date": "2023-01-01 00:00:00.000",
                    "last_modif_date": "2023-01-01 00:00:00.000",
                }
            }
        ),
        encoding="utf-8",
    )

    insert_calls = []
    modify_calls = []
    monkeypatch.setattr(command_module, "insert_command_db", lambda *args, **kwargs: insert_calls.append(args))
    monkeypatch.setattr(command_module, "modify_command_db", lambda *args, **kwargs: modify_calls.append(args))

    table.import_commands(str(import_file))

    assert insert_calls == []
    assert modify_calls == []


def test_import_existing_command_with_changes_and_accepts_replace(tmp_path, monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {
        "echo hi": {
            "description": "old",
            "tag": "old-tag",
            "creation_date": "2023-01-01 00:00:00.000",
            "last_modif_date": "2023-01-01 00:00:00.000",
        }
    }

    import_file = tmp_path / "import.json"
    import_file.write_text(
        json.dumps(
            {
                "echo hi": {
                    "description": "new",
                    "tag": "new-tag",
                    "creation_date": "2023-01-01 00:00:00.000",
                    "last_modif_date": "2023-01-02 00:00:00.000",
                }
            }
        ),
        encoding="utf-8",
    )

    modify_calls = []
    monkeypatch.setattr(command_module.Prompt, "ask", lambda _: "y")
    monkeypatch.setattr(
        command_module,
        "modify_command_db",
        lambda *args, **kwargs: modify_calls.append(args),
    )
    monkeypatch.setattr(command_module, "print", lambda *args, **kwargs: None)

    table.import_commands(str(import_file))

    assert len(modify_calls) == 1
    assert modify_calls[0][0] == "echo hi"
    assert modify_calls[0][1] == "new"
    assert modify_calls[0][2] == "new-tag"


def test_import_existing_command_replace_prompt_prints_command_name(tmp_path, monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {
        "echo hi": {
            "description": "old",
            "tag": "old-tag",
            "creation_date": "2023-01-01 00:00:00.000",
            "last_modif_date": "2023-01-01 00:00:00.000",
        }
    }

    import_file = tmp_path / "import.json"
    import_file.write_text(
        json.dumps(
            {
                "echo hi": {
                    "description": "new",
                    "tag": "new-tag",
                    "creation_date": "2023-01-01 00:00:00.000",
                    "last_modif_date": "2023-01-02 00:00:00.000",
                }
            }
        ),
        encoding="utf-8",
    )

    messages = []
    monkeypatch.setattr(command_module.Prompt, "ask", lambda _: "n")
    monkeypatch.setattr(command_module, "print", lambda *args, **kwargs: messages.append(args[0]))

    table.import_commands(str(import_file))

    assert "The command [bold green]echo hi[/bold green] already exists in the database:" in messages


def test_import_existing_command_with_changes_and_declines_replace(tmp_path, monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {
        "echo hi": {
            "description": "old",
            "tag": "old-tag",
            "creation_date": "2023-01-01 00:00:00.000",
            "last_modif_date": "2023-01-01 00:00:00.000",
        }
    }

    import_file = tmp_path / "import.json"
    import_file.write_text(
        json.dumps(
            {
                "echo hi": {
                    "description": "new",
                    "tag": "new-tag",
                    "creation_date": "2023-01-01 00:00:00.000",
                    "last_modif_date": "2023-01-02 00:00:00.000",
                }
            }
        ),
        encoding="utf-8",
    )

    modify_calls = []
    monkeypatch.setattr(command_module.Prompt, "ask", lambda _: "n")
    monkeypatch.setattr(
        command_module,
        "modify_command_db",
        lambda *args, **kwargs: modify_calls.append(args),
    )

    table.import_commands(str(import_file))

    assert modify_calls == []


def test_export_commands_raises_when_write_fails(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {"echo hi": {"description": "desc", "tag": "tag", "uid": "id-1"}}

    def fail_open(*args, **kwargs):
        raise OSError("cannot write")

    monkeypatch.setattr(command_module, "print", lambda *args, **kwargs: None)
    monkeypatch.setattr(builtins, "open", fail_open)

    with pytest.raises(OSError):
        table.export_commands()
