import sqlite3
import uuid
import base64
from pathlib import Path
import datetime
import shutil

# Specify the directory and file name
schema_directory = "clir/config/db/"
schema_file_name = "schema.sql"
db_file_name = "clir.db"
sql_schema_path = Path(schema_directory) / schema_file_name
db_user_version = 1

env_path = Path('~').expanduser() / Path(".clir")
db_file = Path(env_path) / db_file_name

def _uuid_to_base64(uuid_obj):
    uuid_bytes = uuid_obj.bytes
    base64_uuid = base64.urlsafe_b64encode(uuid_bytes).rstrip(b'=').decode('ascii')
    return str(base64_uuid)


def _base64_to_uuid(base64_uuid):
    padding = '=' * (4 - len(base64_uuid) % 4)  # Add padding if necessary
    uuid_bytes = base64.urlsafe_b64decode(base64_uuid + padding)
    return str(uuid.UUID(bytes=uuid_bytes))

def _verify_tag_exists(tag: str):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Check if tag exists
    cursor.execute("SELECT * FROM tags WHERE tag = ?", (tag,))
    tag_exists = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    if not tag_exists:
        tag_uuid = _uuid_to_base64(uuid.uuid4())

        # Insert a new tag into the database
        insert_tag(tag = tag, tag_uuid = tag_uuid)
    else:
        tag_uuid = cursor.execute("SELECT id FROM tags WHERE tag = ?", (tag,))
    
    return tag_uuid

def _verify_command_exists(command: str):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Check if command exists
    cursor.execute("SELECT * FROM commands WHERE command = ?", (command,))
    command_exists = cursor.fetchone()

    if command_exists:
        command_uuid = cursor.execute("SELECT id FROM commands WHERE command = ?", (command,))
    else:
        return False

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return command_uuid

# Creates the DB from the schema file
def create_database(database_name = db_file, schema_file = sql_schema_path):
    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(database_name)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Read and execute SQL statements from the schema file
    with open(schema_file, 'r') as schema_file:
        schema_sql = schema_file.read()
        #print(schema_sql)
        cursor.executescript(schema_sql)
        
    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

# Insert a new command into the database
def insert_command(command: str, description: str, tag: str = ""):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    command_uuid = _uuid_to_base64(uuid.uuid4())
    tag_uuid = ""

    creation_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    last_modif_date = creation_date

    tag_uuid = _verify_tag_exists(tag)

    command_exists = _verify_command_exists(command)

    if command_exists:
        modify_command(command, description, tag)
    else:
        # Insert a new command into the database
        cursor.execute("INSERT INTO commands (command, description, id, creation_date, last_modif_date) VALUES (?, ?, ?, ?, ?)", (command, description, command_uuid, creation_date, last_modif_date))

    # Insert a new command into the commands_tags table
    cursor.execute("INSERT INTO commands_tags (command_id, tag_id) VALUES (?, ?)", (command_uuid, tag_uuid))

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

# Modify a command in the database
def modify_command(command: str, description: str, tag: str = ""):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    command_uuid = _uuid_to_base64(uuid.uuid4())
    tag_uuid = ""

    last_modif_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    tag_uuid = _verify_tag_exists(tag)

    # Modify the command in the database
    cursor.execute("UPDATE commands SET description = ?, last_modif_date = ? WHERE command = ?", (description, last_modif_date, command))

    # Modify the command in the commands_tags table
    cursor.execute("UPDATE commands_tags SET tag_id = ? WHERE command_id = ?", (tag_uuid, command_uuid))

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

# Remove a command from the database
def remove_command(command: str):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Remove a command from the database
    cursor.execute("DELETE FROM commands WHERE command = ?", (command,))

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

# Get all commands from the database
def get_commands(tag: str = "", grep: str = ""):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Get all commands from the database
    if tag:
        cursor.execute("SELECT * FROM commands WHERE tag = ?", (tag,))
    elif grep:
        cursor.execute("SELECT * FROM commands WHERE command LIKE ?", (f"%{grep}%",))
    else:
        cursor.execute("SELECT * FROM commands")

    commands = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return commands

# Get all tags from the database
def get_tags(grep: str = ""):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Get all tags from the database
    if grep:
        cursor.execute("SELECT * FROM tags WHERE tag LIKE ?", (f"%{grep}%",))
    else:
        cursor.execute("SELECT * FROM tags")

    tags = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return tags

# Insert a new tag into the database
def insert_tag(tag: str, tag_uuid: str = _uuid_to_base64(uuid.uuid4())):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    creation_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    last_modif_date = creation_date

    # Insert a new tag into the database
    cursor.execute("INSERT INTO tags (tag, id, creation_date, last_modif_date) VALUES (?, ?, ?, ?)", (tag, tag_uuid, creation_date, last_modif_date))

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return tag_uuid

# Remove a tag from the database
def remove_tag(tag: str):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Remove a tag from the database
    cursor.execute("DELETE FROM tags WHERE tag = ?", (tag,))

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

