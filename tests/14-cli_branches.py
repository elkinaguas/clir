from click.testing import CliRunner

import clir.cli as cli_module


def test_cli_group_callback_executes_pass():
    callback = getattr(cli_module.cli, "callback")
    assert callback() is None


def test_tags_command_calls_show_tags(monkeypatch):
    runner = CliRunner()
    calls = {}

    class FakeTable:
        def __init__(self, tag="", grep="", tag_grep=""):
            calls["grep"] = grep
            calls["tag_grep"] = tag_grep

        def show_tags(self):
            calls["show_tags"] = True

    def fake_init():
        calls["init"] = calls.get("init", 0) + 1

    monkeypatch.setattr(cli_module, "init_config", fake_init)
    monkeypatch.setattr(cli_module, "CommandTable", FakeTable)

    result = runner.invoke(cli_module.tags, ["-g", "ops"])

    assert result.exit_code == 0
    assert calls["init"] == 1
    assert calls["grep"] == ""
    assert calls["tag_grep"] == "ops"
    assert calls["show_tags"] is True


def test_imports_prompts_until_file_and_imports(monkeypatch):
    runner = CliRunner()
    calls = {}
    calls["prompt_count"] = 0

    class FakeTable:
        def __init__(self, *args, **kwargs):
            return None

        def import_commands(self, import_file_path=""):
            calls["import_file_path"] = import_file_path

    answers = iter(["", "commands.json"])

    def fake_ask(_):
        calls["prompt_count"] += 1
        return next(answers)

    def fake_init():
        calls["init"] = calls.get("init", 0) + 1

    monkeypatch.setattr(cli_module, "init_config", fake_init)
    monkeypatch.setattr(cli_module, "CommandTable", FakeTable)
    monkeypatch.setattr(cli_module.Prompt, "ask", fake_ask)

    result = runner.invoke(cli_module.imports)

    assert result.exit_code == 0
    assert calls["init"] == 1
    assert calls["prompt_count"] == 2
    assert calls["import_file_path"] == "commands.json"


def test_settings_calls_init_config(monkeypatch):
    runner = CliRunner()
    calls = {"init": 0}

    def fake_init():
        calls["init"] += 1

    monkeypatch.setattr(cli_module, "init_config", fake_init)

    result = runner.invoke(cli_module.settings)

    assert result.exit_code == 0
    assert calls["init"] == 1


def test_imports_shows_click_error_for_missing_file(monkeypatch):
    runner = CliRunner()
    calls = {"init": 0}

    class FakeTable:
        def import_commands(self, import_file_path=""):
            raise FileNotFoundError(f"File '{import_file_path}' could not be found")

    def fake_init():
        calls["init"] += 1

    monkeypatch.setattr(cli_module, "init_config", fake_init)
    monkeypatch.setattr(cli_module, "CommandTable", lambda: FakeTable())

    result = runner.invoke(cli_module.imports, ["-f", "missing.json"])

    assert result.exit_code == 1
    assert calls["init"] == 1
    assert "File 'missing.json' could not be found" in result.output


def test_imports_shows_click_error_for_invalid_payload(monkeypatch):
    runner = CliRunner()
    calls = {"init": 0}

    class FakeTable:
        def import_commands(self, import_file_path=""):
            raise ValueError("Import payload must be a JSON object mapping commands to metadata")

    def fake_init():
        calls["init"] += 1

    monkeypatch.setattr(cli_module, "init_config", fake_init)
    monkeypatch.setattr(cli_module, "CommandTable", lambda: FakeTable())

    result = runner.invoke(cli_module.imports, ["-f", "broken.json"])

    assert result.exit_code == 1
    assert calls["init"] == 1
    assert "Import payload must be a JSON object mapping commands to metadata" in result.output
