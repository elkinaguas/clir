import sqlite3
import uuid
import base64
from pathlib import Path
import datetime
import shutil
import importlib.resources

# Specify the directory and file name
schema_directory = "clir/config/db/"
schema_file_name = "schema.sql"
db_file_name = "clir.db"
sql_schema_path = Path(schema_directory) / schema_file_name
db_user_version = 1

env_path = Path('~').expanduser() / Path(".clir")
db_file = Path(env_path) / db_file_name

def _verify_tag_exists(tag: str):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Check if tag exists
    cursor.execute("SELECT * FROM tags WHERE tag = ?", (tag,))
    tag_exists = cursor.fetchone()

    if not tag_exists:
        tag_uuid = str(uuid.uuid4())

        # Insert a new tag into the database
        insert_tag(tag = tag, tag_uuid = tag_uuid)
    else:
        tag_uuid = cursor.execute("SELECT id FROM tags WHERE tag = ?", (tag,))
        tag_uuid = cursor.fetchone()[0]
    
    # Close the cursor and connection
    cursor.close()
    conn.close()

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
    with importlib.resources.open_text('clir.config.db', 'schema.sql') as f:
        schema = f.read()
        cursor.executescript(schema)
        
    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

# Insert a new command into the database
def insert_command_db(command: str, description: str, tag: str = "", creation_date: str = "", last_modif_date: str = ""):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    command_uuid = str(uuid.uuid4())
    tag_uuid = ""

    if not creation_date and not last_modif_date:
        creation_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        last_modif_date = creation_date
    elif creation_date and not last_modif_date:
        last_modif_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    elif not creation_date and last_modif_date:
        creation_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    tag_uuid = _verify_tag_exists(tag)

    command_exists = _verify_command_exists(command)

    if command_exists:
        modify_command_db(command, description, tag)
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

    return 0

# Modify a command in the database
def modify_command_db(command: str, description: str, tag: str = "", creation_date: str = "", last_modif_date: str = ""):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    command_uuid = cursor.execute("SELECT id FROM commands WHERE command = ?", (command,))
    command_uuid = cursor.fetchone()[0]
    tag_uuid = ""

    if not last_modif_date:
        last_modif_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    if creation_date:
        # Modify the command in the database
        cursor.execute("UPDATE commands SET description = ?, creation_date = ?, last_modif_date = ? WHERE command = ?", (description, creation_date, last_modif_date, command))
    else:
        # Modify the command in the database
        cursor.execute("UPDATE commands SET description = ?, last_modif_date = ? WHERE command = ?", (description, last_modif_date, command))

    tag_uuid = _verify_tag_exists(tag)

    # Modify the command in the commands_tags table
    cursor.execute("UPDATE commands_tags SET tag_id = ? WHERE command_id = ?", (tag_uuid, command_uuid))

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return 0


# Remove a command from the database
def remove_command_db(uid: str):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Remove a command from the database
    cursor.execute("DELETE FROM commands WHERE id = ?", (uid,))
    cursor.execute("DELETE FROM commands_tags WHERE command_id = ?", (uid,))

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

def verify_command_id_exists(uid: str):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Check if command exists
    cursor.execute("SELECT * FROM commands WHERE id = ?", (uid,))
    command_exists = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return True if command_exists else False

def verify_tag_id_exists(uid: str):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Check if tag exists
    cursor.execute("SELECT * FROM tags WHERE id = ?", (uid,))
    tag_exists = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return True if tag_exists else False

def verify_command_id_tag_relation_exists(command_id: str):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Check if command_id exists in the commands_tags table
    cursor.execute("SELECT * FROM commands_tags WHERE command_id = ?", (command_id,))
    command_id_exists = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return True if command_id_exists else False

# Get all commands from the database
def get_commands_db(tag: str = "", grep: str = ""):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Get all commands from the database
    if tag:
        command_ids = get_commands_from_tag(tag)
        query = "SELECT * FROM commands WHERE id IN ({})".format(','.join('?' for _ in command_ids))
        cursor.execute(query, command_ids)
    elif grep:
        cursor.execute("SELECT * FROM commands WHERE command LIKE ? OR description LIKE ?", (f"%{grep}%", f"%{grep}%"))
    else:
        cursor.execute("SELECT * FROM commands")

    commands = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return commands

# Get all tags from the database
def get_tags_db(grep: str = ""):
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
def insert_tag(tag: str, tag_uuid: str = str(uuid.uuid4())):
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

def get_command_id_from_command(command):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Get the command_id from the commands table
    cursor.execute("SELECT id FROM commands WHERE command = ?", (command,))
    command_id = cursor.fetchone()[0]

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return command_id

def get_tag_id_from_command_id(command_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Get the tag_id from the commands_tags table
    cursor.execute("SELECT * FROM commands_tags WHERE command_id = ?", (command_id,))
    tag_id = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return tag_id

def get_tag_from_tag_id(tag_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    query = "SELECT tag FROM tags WHERE id IN ({})".format(','.join('?' for _ in tag_id))
    cursor.execute(query, tag_id)

    tag = cursor.fetchall()[0][0]
    #tags = [row[0] for row in tag]

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return tag

def get_tag_id_from_tag(tag):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    tag_id = ""

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Get the tag_id from the tags table
    cursor.execute("SELECT id FROM tags WHERE tag = ?", (tag,))
    try :
        tag_id = cursor.fetchone()[0]
    except:
        pass

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return tag_id

def get_command_ids_from_tag_id(tag_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Get the command_id from the commands_tags table
    cursor.execute("SELECT * FROM commands_tags WHERE tag_id = ?", (tag_id,))
    command_ids = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return [id[0] for id in command_ids]

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
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Get all commands from the database
        cursor.execute("SELECT id FROM commands")

        self.commands_ids = [command_id[0] for command_id in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return self.commands_ids
    
    def get_commands(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Get all commands from the database
        cursor.execute("SELECT command FROM commands")

        self.commands = [command[0] for command in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return self.commands

    def get_tags_ids(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Get all tags from the database
        cursor.execute("SELECT id FROM tags")

        self.tags_ids = [tag_id[0] for tag_id in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return self.tags_ids
    
    def get_tags(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Get all tags from the database
        cursor.execute("SELECT tag FROM tags")

        self.tags = [tag[0] for tag in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return self.tags
    
    def get_commands_ids_relation(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Get all tags from the database
        cursor.execute("SELECT command_id FROM commands_tags")

        command_tag_relation = [command_id[0] for command_id in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return command_tag_relation

    def get_tags_ids_relation(self):
        # Connect to the SQLite database
        conn = sqlite3.connect(db_file)

        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # Get all tags from the database
        cursor.execute("SELECT tag_id FROM commands_tags")

        tag_command_relation = [tag_id[0] for tag_id in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        conn.close()

        return tag_command_relation

    def main(self):
        return self.get_commands_ids(), self.get_commands(), self.get_tags_ids(), self.get_tags(), self.get_commands_ids_relation(), self.get_tags_ids_relation()