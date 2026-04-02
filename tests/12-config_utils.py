from clir.utils import config as config_module


def test_create_config_files_creates_commands_json(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    config_module.create_config_files()

    commands_file = tmp_path / ".clir" / "commands.json"
    assert commands_file.exists()
    assert commands_file.read_text(encoding="utf-8") == "{}"


def test_check_config_uses_current_home_at_call_time(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    clir_dir = tmp_path / ".clir"
    clir_dir.mkdir(parents=True)
    (clir_dir / "clir.db").write_text("db", encoding="utf-8")
    (clir_dir / "clir.conf").write_text("conf", encoding="utf-8")

    assert config_module.check_config() is True


def test_create_config_files_keeps_existing_commands_json(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    clir_dir = tmp_path / ".clir"
    clir_dir.mkdir(parents=True)
    commands_file = clir_dir / "commands.json"
    commands_file.write_text('{"existing": true}', encoding="utf-8")

    config_module.create_config_files()

    assert commands_file.read_text(encoding="utf-8") == '{"existing": true}'


def test_copy_config_files_uses_current_home_at_call_time(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))

    config_module.copy_config_files()

    assert (tmp_path / ".clir" / "clir.conf").exists()


def test_init_config_returns_when_setup_cannot_be_completed(monkeypatch):
    calls = []

    monkeypatch.setattr(config_module, "check_config", lambda: False)
    monkeypatch.setattr(config_module, "create_database", lambda: calls.append("create_database"))
    monkeypatch.setattr(config_module, "create_config_files", lambda: calls.append("create_config_files"))
    monkeypatch.setattr(config_module, "copy_config_files", lambda: calls.append("copy_config_files"))
    monkeypatch.setattr(config_module, "migrate_json_to_sqlite", lambda: calls.append("migrate_json_to_sqlite"))

    result = config_module.init_config()

    assert result is None
    assert calls == [
        "create_database",
        "create_config_files",
        "copy_config_files",
        "migrate_json_to_sqlite",
    ]


def test_init_config_repairs_empty_config_file(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    clir_dir = tmp_path / ".clir"
    clir_dir.mkdir(parents=True)
    (clir_dir / "clir.db").write_text("db", encoding="utf-8")
    (clir_dir / "clir.conf").write_text("", encoding="utf-8")

    config_module.init_config()

    repaired_config = (clir_dir / "clir.conf").read_text(encoding="utf-8")
    backup_file = clir_dir / "clir.conf.backup"

    assert 'default_current_folder' in repaired_config
    assert backup_file.exists()
    assert backup_file.read_text(encoding="utf-8") == ""


def test_read_setting_repairs_invalid_config_file(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    clir_dir = tmp_path / ".clir"
    clir_dir.mkdir(parents=True)
    (clir_dir / "clir.conf").write_text("not-json", encoding="utf-8")

    value = config_module.read_setting("default_current_folder")

    assert value is False
    assert (clir_dir / "clir.conf.backup").exists()


def test_verify_clipboard_tool_installation_xclip_true(monkeypatch):
    monkeypatch.setattr(config_module.shutil, "which", lambda package: f"/usr/bin/{package}")

    assert config_module.verify_clipboard_tool_installation("xclip") is True


def test_verify_clipboard_tool_installation_xclip_false_on_error(monkeypatch):
    monkeypatch.setattr(config_module.shutil, "which", lambda package: None)

    assert config_module.verify_clipboard_tool_installation("xclip") is False


def test_verify_clipboard_tool_installation_pbcopy_true(monkeypatch):
    monkeypatch.setattr(config_module.shutil, "which", lambda package: f"/usr/bin/{package}")

    assert config_module.verify_clipboard_tool_installation("pbcopy") is True


def test_verify_clipboard_tool_installation_pbcopy_false_on_error(monkeypatch):
    monkeypatch.setattr(config_module.shutil, "which", lambda package: None)

    assert config_module.verify_clipboard_tool_installation("pbcopy") is False


def test_verify_clipboard_tool_installation_without_package_returns_false():
    assert config_module.verify_clipboard_tool_installation() is False
