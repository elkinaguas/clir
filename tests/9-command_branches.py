from clir.command import Command
from clir.command import CommandTable
import clir.command as command_module


def test_save_command_uses_default_tag_when_empty(monkeypatch):
    captured = {}

    def fake_insert(command, description, tag, *args):
        captured["command"] = command
        captured["description"] = description
        captured["tag"] = tag

    monkeypatch.setattr(command_module, "get_commands_db", lambda *args, **kwargs: [])
    monkeypatch.setattr(command_module, "insert_command_db", fake_insert)

    cmd = Command(command="echo hi", description="print hi", tag="")
    cmd.save_command()

    assert captured == {
        "command": "echo hi",
        "description": "print hi",
        "tag": "clir",
    }


def test_get_command_uid_returns_empty_for_non_integer(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {"echo hi": {"uid": "uid-1"}}

    monkeypatch.setattr(CommandTable, "show_table", lambda self: None)
    monkeypatch.setattr(command_module.Prompt, "ask", lambda _: "abc")

    assert table.get_command_uid() == ""


def test_copy_command_uses_pbcopy_on_darwin(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {"echo hello": {"uid": "uid-1"}}

    calls = []
    monkeypatch.setattr(CommandTable, "get_command_uid", lambda self: "uid-1")
    monkeypatch.setattr(command_module.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(command_module, "verify_xclip_installation", lambda package: True)
    monkeypatch.setattr(command_module.os, "system", lambda cmd: calls.append(cmd))

    table.copy_command()

    assert calls == ['printf "echo hello" | pbcopy']


def test_copy_command_shows_missing_tool_on_linux(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {"echo hello": {"uid": "uid-1"}}

    calls = []
    monkeypatch.setattr(CommandTable, "get_command_uid", lambda self: "uid-1")
    monkeypatch.setattr(command_module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(command_module, "verify_xclip_installation", lambda package: False)
    monkeypatch.setattr(command_module.os, "system", lambda cmd: calls.append(cmd))

    table.copy_command()

    assert calls == []


def test_copy_command_handles_unsupported_os(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {"echo hello": {"uid": "uid-1"}}

    calls = []
    monkeypatch.setattr(CommandTable, "get_command_uid", lambda self: "uid-1")
    monkeypatch.setattr(command_module.platform, "system", lambda: "Windows")
    monkeypatch.setattr(command_module.os, "system", lambda cmd: calls.append(cmd))

    table.copy_command()

    assert calls == []


def test_run_command_executes_replaced_command(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {"echo @name": {"uid": "uid-1"}}

    executed = []
    history_calls = []

    monkeypatch.setattr(CommandTable, "get_command_uid", lambda self: "uid-1")
    monkeypatch.setattr(command_module, "replace_arguments", lambda cmd: "echo alice")
    monkeypatch.setattr(command_module.os, "system", lambda cmd: executed.append(cmd))
    monkeypatch.setattr(
        command_module.subprocess,
        "Popen",
        lambda args: history_calls.append(args),
    )

    table.run_command()

    assert executed == ["echo alice"]
    assert history_calls == [["bash", "-ic", 'set -o history; history -s "$1"', "_", "echo alice"]]


def test_command_str_and_repr_include_fields():
    cmd = Command(command="echo hi", description="desc", tag="ops")

    assert str(cmd) == "echo hi desc ops"
    assert repr(cmd) == "echo hi desc ops"


def test_command_table_str_and_repr_with_manual_fields():
    table = object.__new__(CommandTable)
    setattr(table, "command", "echo hi")
    setattr(table, "description", "desc")
    setattr(table, "tag", "ops")

    assert str(table) == "echo hi desc ops"
    assert repr(table) == "echo hi desc ops"


def test_copy_command_shows_missing_pbcopy_on_darwin(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {"echo hello": {"uid": "uid-1"}}

    calls = []
    monkeypatch.setattr(CommandTable, "get_command_uid", lambda self: "uid-1")
    monkeypatch.setattr(command_module.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(command_module, "verify_xclip_installation", lambda package: False)
    monkeypatch.setattr(command_module.os, "system", lambda cmd: calls.append(cmd))

    table.copy_command()

    assert calls == []


def test_copy_command_linux_uses_xclip_when_available(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {"echo hello": {"uid": "uid-1"}}

    calls = []
    monkeypatch.setattr(CommandTable, "get_command_uid", lambda self: "uid-1")
    monkeypatch.setattr(command_module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(command_module, "verify_xclip_installation", lambda package: True)
    monkeypatch.setattr(command_module.os, "system", lambda cmd: calls.append(cmd))

    table.copy_command()

    assert calls == ['echo -n "echo hello" | xclip -selection clipboard']


def test_show_tags_renders_unique_tags(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {
        "echo one": {"tag": "ops", "uid": "1", "description": "a"},
        "echo two": {"tag": "ops", "uid": "2", "description": "b"},
        "echo three": {"tag": "dev", "uid": "3", "description": "c"},
    }

    class DummyConsole:
        def print(self, _table):
            return None

    monkeypatch.setattr(command_module, "Console", DummyConsole)

    table.show_tags()


def test_import_commands_without_file_is_noop(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {}
    monkeypatch.setattr(command_module, "print", lambda *args, **kwargs: None)

    table.import_commands("")


def test_remove_command_reports_when_command_still_exists(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {}

    monkeypatch.setattr(CommandTable, "get_command_uid", lambda self: "uid-1")
    monkeypatch.setattr(command_module, "get_tags_db", lambda: [("tag-1",)])
    monkeypatch.setattr(command_module, "remove_command_db", lambda uid: None)
    monkeypatch.setattr(command_module, "verify_command_id_exists", lambda uid: True)
    monkeypatch.setattr(command_module, "remove_tag_if_no_commands", lambda tag_uids: None)

    table.remove_command()


def test_remove_command_reports_relation_not_removed(monkeypatch):
    table = object.__new__(CommandTable)
    table.commands = {}

    monkeypatch.setattr(CommandTable, "get_command_uid", lambda self: "uid-1")
    monkeypatch.setattr(command_module, "get_tags_db", lambda: [("tag-1",)])
    monkeypatch.setattr(command_module, "remove_command_db", lambda uid: None)
    monkeypatch.setattr(command_module, "verify_command_id_exists", lambda uid: False)
    monkeypatch.setattr(command_module, "verify_command_id_tag_relation_exists", lambda uid: True)
    monkeypatch.setattr(command_module, "remove_tag_if_no_commands", lambda tag_uids: None)

    table.remove_command()
