import sqlite3
from uuid import uuid4

from clir.utils import db as db_module


def _setup_temp_db(monkeypatch, tmp_path):
    temp_db = tmp_path / "clir.db"
    monkeypatch.setattr(db_module, "db_file", temp_db)
    db_module.create_database(database_name=temp_db)
    return temp_db


def test_insert_command_db_sets_last_modif_when_only_creation_date(monkeypatch, tmp_path):
    temp_db = _setup_temp_db(monkeypatch, tmp_path)

    db_module.insert_command_db(
        command="echo created",
        description="desc",
        tag="ops",
        creation_date="2024-01-01 00:00:00.000",
        last_modif_date="",
    )

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT creation_date, last_modif_date FROM commands WHERE command = ?", ("echo created",))
    creation_date, last_modif_date = cursor.fetchone()
    cursor.close()
    conn.close()

    assert creation_date == "2024-01-01 00:00:00.000"
    assert last_modif_date


def test_db_connection_enables_foreign_keys(monkeypatch, tmp_path):
    temp_db = _setup_temp_db(monkeypatch, tmp_path)

    with db_module._db_connection(temp_db) as conn:
        pragma_value = conn.execute("PRAGMA foreign_keys").fetchone()[0]

    assert pragma_value == 1


def test_insert_command_db_sets_creation_when_only_last_modif_date(monkeypatch, tmp_path):
    temp_db = _setup_temp_db(monkeypatch, tmp_path)

    db_module.insert_command_db(
        command="echo modified",
        description="desc",
        tag="ops",
        creation_date="",
        last_modif_date="2024-01-02 00:00:00.000",
    )

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT creation_date, last_modif_date FROM commands WHERE command = ?", ("echo modified",))
    creation_date, last_modif_date = cursor.fetchone()
    cursor.close()
    conn.close()

    assert creation_date
    assert last_modif_date == "2024-01-02 00:00:00.000"


def test_modify_command_db_updates_creation_date_when_provided(monkeypatch, tmp_path):
    temp_db = _setup_temp_db(monkeypatch, tmp_path)

    db_module.insert_command_db("echo before", "old", "old-tag")
    db_module.modify_command_db(
        command="echo before",
        description="new",
        tag="old-tag",
        creation_date="2020-05-01 10:11:12.000",
    )

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT description, creation_date FROM commands WHERE command = ?", ("echo before",))
    description, creation_date = cursor.fetchone()
    cursor.close()
    conn.close()

    assert description == "new"
    assert creation_date == "2020-05-01 10:11:12.000"


def test_verify_tag_id_exists_true_and_false(monkeypatch, tmp_path):
    _setup_temp_db(monkeypatch, tmp_path)

    tag_uuid = db_module.insert_tag("my-tag")

    assert db_module.verify_tag_id_exists(tag_uuid) is True
    assert db_module.verify_tag_id_exists(str(uuid4())) is False


def test_get_tags_db_filters_with_grep(monkeypatch, tmp_path):
    _setup_temp_db(monkeypatch, tmp_path)

    db_module.insert_tag("ops-prod", str(uuid4()))
    db_module.insert_tag("dev-local", str(uuid4()))

    tags = db_module.get_tags_db(grep="ops")
    tag_names = [row[3] for row in tags]

    assert tag_names == ["ops-prod"]


def test_remove_tag_deletes_tag(monkeypatch, tmp_path):
    _setup_temp_db(monkeypatch, tmp_path)

    tag_uuid = db_module.insert_tag("remove-me")
    assert db_module.verify_tag_id_exists(tag_uuid) is True

    db_module.remove_tag("remove-me")

    assert db_module.verify_tag_id_exists(tag_uuid) is False


def test_get_tag_id_from_tag_returns_empty_when_missing(monkeypatch, tmp_path):
    _setup_temp_db(monkeypatch, tmp_path)

    assert db_module.get_tag_id_from_tag("missing-tag") == ""


def test_get_tag_from_tag_id_returns_empty_when_missing(monkeypatch, tmp_path):
    _setup_temp_db(monkeypatch, tmp_path)

    assert db_module.get_tag_from_tag_id(()) == ""


def test_get_tag_from_tag_id_accepts_string(monkeypatch, tmp_path):
    _setup_temp_db(monkeypatch, tmp_path)

    tag_uuid = db_module.insert_tag("ops")

    assert db_module.get_tag_from_tag_id(tag_uuid) == "ops"
