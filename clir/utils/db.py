import datetime
import importlib.resources
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path

# Specify the directory and file name
schema_directory = "clir/config/db/"
schema_file_name = "schema.sql"
db_file_name = "clir.db"
sql_schema_path = Path(schema_directory) / schema_file_name
db_user_version = 1

env_path = Path('~').expanduser() / Path(".clir")
db_file = Path(env_path) / db_file_name


def _timestamp_now() -> str:
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


@contextmanager
def _db_connection(database_name=None):
    connection = sqlite3.connect(database_name or db_file)
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _fetchone(query: str, params=(), database_name=None):
    with _db_connection(database_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchone()
        finally:
            cursor.close()


def _fetchall(query: str, params=(), database_name=None):
    with _db_connection(database_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        finally:
            cursor.close()


def _execute(query: str, params=(), database_name=None):
    with _db_connection(database_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
        finally:
            cursor.close()


def _select_ids_query(table_name: str, column_name: str, values):
    allowed_tables = {"commands", "tags"}
    allowed_columns = {"*", "id", "tag"}

    if table_name not in allowed_tables:
        raise ValueError(f"Unsupported table name: {table_name}")
    if column_name not in allowed_columns:
        raise ValueError(f"Unsupported column name: {column_name}")

    placeholders = ','.join('?' for _ in values)
    return f"SELECT {column_name} FROM {table_name} WHERE id IN ({placeholders})"

def _verify_tag_exists(tag: str):
    tag_row = _fetchone("SELECT id FROM tags WHERE tag = ?", (tag,))

    if not tag_row:
        return insert_tag(tag=tag, tag_uuid=str(uuid.uuid4()))

    return tag_row[0]

def _verify_command_exists(command: str):
    command_row = _fetchone("SELECT id FROM commands WHERE command = ?", (command,))
    return command_row[0] if command_row else False

# Creates the DB from the schema file
def create_database(database_name=None, schema_file=sql_schema_path):
    del schema_file

    with _db_connection(database_name) as conn:
        cursor = conn.cursor()
        try:
            with importlib.resources.open_text('clir.config.db', 'schema.sql') as f:
                cursor.executescript(f.read())
        finally:
            cursor.close()

# Insert a new command into the database
def insert_command_db(command: str, description: str, tag: str = "", creation_date: str = "", last_modif_date: str = ""):
    command_uuid = str(uuid.uuid4())

    if not creation_date and not last_modif_date:
        creation_date = _timestamp_now()
        last_modif_date = creation_date
    elif creation_date and not last_modif_date:
        last_modif_date = _timestamp_now()
    elif not creation_date and last_modif_date:
        creation_date = _timestamp_now()

    tag_uuid = _verify_tag_exists(tag)

    command_exists = _verify_command_exists(command)

    if command_exists:
        modify_command_db(command, description, tag)
    else:
        with _db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO commands (command, description, id, creation_date, last_modif_date) VALUES (?, ?, ?, ?, ?)",
                    (command, description, command_uuid, creation_date, last_modif_date),
                )
                cursor.execute(
                    "INSERT INTO commands_tags (command_id, tag_id) VALUES (?, ?)",
                    (command_uuid, tag_uuid),
                )
            finally:
                cursor.close()

    return 0

# Modify a command in the database
def modify_command_db(command: str, description: str, tag: str = "", creation_date: str = "", last_modif_date: str = ""):
    command_uuid = get_command_id_from_command(command)

    if not last_modif_date:
        last_modif_date = _timestamp_now()

    tag_uuid = _verify_tag_exists(tag)

    with _db_connection() as conn:
        cursor = conn.cursor()
        try:
            if creation_date:
                cursor.execute(
                    "UPDATE commands SET description = ?, creation_date = ?, last_modif_date = ? WHERE command = ?",
                    (description, creation_date, last_modif_date, command),
                )
            else:
                cursor.execute(
                    "UPDATE commands SET description = ?, last_modif_date = ? WHERE command = ?",
                    (description, last_modif_date, command),
                )

            cursor.execute(
                "UPDATE commands_tags SET tag_id = ? WHERE command_id = ?",
                (tag_uuid, command_uuid),
            )
        finally:
            cursor.close()

    return 0


# Remove a command from the database
def remove_command_db(uid: str):
    with _db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM commands_tags WHERE command_id = ?", (uid,))
            cursor.execute("DELETE FROM commands WHERE id = ?", (uid,))
        finally:
            cursor.close()

def verify_command_id_exists(uid: str):
    return _fetchone("SELECT 1 FROM commands WHERE id = ?", (uid,)) is not None

def verify_tag_id_exists(uid: str):
    return _fetchone("SELECT 1 FROM tags WHERE id = ?", (uid,)) is not None

def verify_command_id_tag_relation_exists(command_id: str):
    return _fetchone("SELECT 1 FROM commands_tags WHERE command_id = ?", (command_id,)) is not None

# Get all commands from the database
def get_commands_db(tag: str = "", grep: str = ""):
    if tag:
        command_ids = get_commands_from_tag(tag)
        if not command_ids:
            return []
        query = _select_ids_query("commands", "*", command_ids)
        return _fetchall(query, tuple(command_ids))
    if grep:
        return _fetchall(
            "SELECT * FROM commands WHERE command LIKE ? OR description LIKE ?",
            (f"%{grep}%", f"%{grep}%"),
        )
    return _fetchall("SELECT * FROM commands")

# Get all tags from the database
def get_tags_db(grep: str = ""):
    if grep:
        return _fetchall("SELECT * FROM tags WHERE tag LIKE ?", (f"%{grep}%",))
    return _fetchall("SELECT * FROM tags")

# Insert a new tag into the database
def insert_tag(tag: str, tag_uuid: str = None):
    if tag_uuid is None:
        tag_uuid = str(uuid.uuid4())

    creation_date = _timestamp_now()
    last_modif_date = creation_date

    with _db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO tags (tag, id, creation_date, last_modif_date) VALUES (?, ?, ?, ?)",
                (tag, tag_uuid, creation_date, last_modif_date),
            )
        finally:
            cursor.close()

    return tag_uuid

# Remove a tag from the database
def remove_tag(tag: str):
    _execute("DELETE FROM tags WHERE tag = ?", (tag,))

def get_command_id_from_command(command):
    return _fetchone("SELECT id FROM commands WHERE command = ?", (command,))[0]

def get_tag_id_from_command_id(command_id):
    return _fetchone("SELECT * FROM commands_tags WHERE command_id = ?", (command_id,))

def get_tag_from_tag_id(tag_id):
    query = _select_ids_query("tags", "tag", tag_id)
    return _fetchall(query, tuple(tag_id))[0][0]

def get_tag_id_from_tag(tag):
    tag_row = _fetchone("SELECT id FROM tags WHERE tag = ?", (tag,))
    return tag_row[0] if tag_row else ""

def get_command_ids_from_tag_id(tag_id):
    command_ids = _fetchall("SELECT * FROM commands_tags WHERE tag_id = ?", (tag_id,))
    return [command_id[0] for command_id in command_ids]

def get_commands_from_tag(tag):
    tag_id = get_tag_id_from_tag(tag)
    command_id = get_command_ids_from_tag_id(tag_id)

    return command_id

# TODO: pass a garbag collector to remove tags that are not used after removing or modifying a command

class DbIntegrity:
    def __init__(self):
        self.commands_ids = ""
        self.commands = ""
        self.tags_ids = ""
        self.tags = ""
    
    def get_commands_ids(self):
        self.commands_ids = [command_id[0] for command_id in _fetchall("SELECT id FROM commands")]

        return self.commands_ids
    
    def get_commands(self):
        self.commands = [command[0] for command in _fetchall("SELECT command FROM commands")]

        return self.commands

    def get_tags_ids(self):
        self.tags_ids = [tag_id[0] for tag_id in _fetchall("SELECT id FROM tags")]

        return self.tags_ids
    
    def get_tags(self):
        self.tags = [tag[0] for tag in _fetchall("SELECT tag FROM tags")]

        return self.tags
    
    def get_commands_ids_relation(self):
        return [command_id[0] for command_id in _fetchall("SELECT command_id FROM commands_tags")]

    def get_tags_ids_relation(self):
        return [tag_id[0] for tag_id in _fetchall("SELECT tag_id FROM commands_tags")]

    def main(self):
        return self.get_commands_ids(), self.get_commands(), self.get_tags_ids(), self.get_tags(), self.get_commands_ids_relation(), self.get_tags_ids_relation()
