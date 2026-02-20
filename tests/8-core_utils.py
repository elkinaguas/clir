import builtins
import os
import uuid
import base64
import json

from clir.utils import core


def test_replace_arguments_reuses_prompt_for_duplicate_tokens(monkeypatch):
    calls = []

    def fake_input(arg):
        calls.append(arg)
        return "VALUE"

    monkeypatch.setattr(core, "get_user_input", fake_input)

    command = "echo @name && printf @name"
    result = core.replace_arguments(command)

    assert result == "echo VALUE && printf VALUE"
    assert calls == ["@name"]


def test_replace_arguments_does_not_touch_email_addresses(monkeypatch):
    monkeypatch.setattr(core, "get_user_input", lambda arg: "ALICE")

    command = "notify test@example.com and @user"
    result = core.replace_arguments(command)

    assert "test@example.com" in result
    assert result.endswith("ALICE")


def test_replace_arguments_without_tokens_returns_original():
    command = "echo hello world"

    assert core.replace_arguments(command) == command


def test_get_commands_returns_empty_list_when_file_missing(monkeypatch):
    original_open = builtins.open

    def fake_open(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(builtins, "open", fake_open)

    result = core.get_commands()

    monkeypatch.setattr(builtins, "open", original_open)
    assert result == []


def test_remove_tag_if_no_commands_removes_when_user_accepts(monkeypatch):
    removed_tags = []

    monkeypatch.setattr(core, "get_command_ids_from_tag_id", lambda tag_id: [])
    monkeypatch.setattr(core, "get_tag_from_tag_id", lambda tag_tuple: f"tag-{tag_tuple[0]}")
    monkeypatch.setattr(core, "remove_tag", lambda tag: removed_tags.append(tag))
    monkeypatch.setattr(core, "verify_tag_id_exists", lambda uid: False)
    monkeypatch.setattr(builtins, "input", lambda _: "y")

    core.remove_tag_if_no_commands(["A", "B"])

    assert removed_tags == ["tag-A", "tag-B"]


def test_remove_tag_if_no_commands_keeps_when_user_declines(monkeypatch):
    removed_tags = []

    monkeypatch.setattr(core, "get_command_ids_from_tag_id", lambda tag_id: [])
    monkeypatch.setattr(core, "get_tag_from_tag_id", lambda tag_tuple: f"tag-{tag_tuple[0]}")
    monkeypatch.setattr(core, "remove_tag", lambda tag: removed_tags.append(tag))
    monkeypatch.setattr(builtins, "input", lambda _: "n")

    core.remove_tag_if_no_commands(["A"])

    assert removed_tags == []


def test_remove_tag_if_no_commands_skips_non_orphan_tags(monkeypatch):
    removed_tags = []

    def fake_command_ids(tag_id):
        if tag_id == "A":
            return ["cmd-id"]
        return []

    monkeypatch.setattr(core, "get_command_ids_from_tag_id", fake_command_ids)
    monkeypatch.setattr(core, "get_tag_from_tag_id", lambda tag_tuple: f"tag-{tag_tuple[0]}")
    monkeypatch.setattr(core, "remove_tag", lambda tag: removed_tags.append(tag))
    monkeypatch.setattr(core, "verify_tag_id_exists", lambda uid: False)
    monkeypatch.setattr(builtins, "input", lambda _: "y")

    core.remove_tag_if_no_commands(["A", "B"])

    assert removed_tags == ["tag-B"]


def test_get_commands_applies_tag_and_grep_filters(tmp_path):
    home = tmp_path
    clir_dir = home / ".clir"
    clir_dir.mkdir()
    commands_file = clir_dir / "commands.json"
    commands_file.write_text(
        json.dumps(
            {
                "echo one": {"tag": "ops", "description": "alpha"},
                "echo two": {"tag": "dev", "description": "beta"},
            }
        ),
        encoding="utf-8",
    )

    original_home = os.environ.get("HOME")
    os.environ["HOME"] = str(home)
    try:
        result = core.get_commands(tag="ops", grep="alpha")
    finally:
        if original_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = original_home

    assert result == {"echo one": {"tag": "ops", "description": "alpha"}}


def test_get_user_input_returns_builtin_input(monkeypatch):
    monkeypatch.setattr(builtins, "input", lambda prompt: "typed-value")

    assert core.get_user_input("@value") == "typed-value"


def test_uuid_base64_round_trip(monkeypatch):
    monkeypatch.setattr(core, "base64", base64, raising=False)
    monkeypatch.setattr(core, "uuid", uuid, raising=False)

    uid = uuid.uuid4()
    encoded = core.uuid_to_base64(uid)
    decoded = core.base64_to_uuid(encoded)

    assert decoded == uid


def test_remove_tag_if_no_commands_reports_not_removed(monkeypatch):
    monkeypatch.setattr(core, "get_command_ids_from_tag_id", lambda tag_id: [])
    monkeypatch.setattr(core, "get_tag_from_tag_id", lambda tag_tuple: "tag-a")
    monkeypatch.setattr(core, "remove_tag", lambda tag: None)
    monkeypatch.setattr(core, "verify_tag_id_exists", lambda uid: True)
    monkeypatch.setattr(builtins, "input", lambda _: "y")

    core.remove_tag_if_no_commands(["A"])


def test_remove_tag_if_no_commands_handles_invalid_response(monkeypatch):
    monkeypatch.setattr(core, "get_command_ids_from_tag_id", lambda tag_id: [])
    monkeypatch.setattr(core, "get_tag_from_tag_id", lambda tag_tuple: "tag-a")
    monkeypatch.setattr(builtins, "input", lambda _: "maybe")

    core.remove_tag_if_no_commands(["A"])
