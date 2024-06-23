import sqlite3
import uuid
from pathlib import Path
#from forevernotes.utils.objects import Note, Tag, NoteTag
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

# TODO: Create script to backup json stored commands before migration
def back_json_commands():
    source_file = f"{env_path}/commands.json"
    destination_file = f"{env_path}/commands.json.backup"

    shutil.copyfile(source_file, destination_file)

    print(f"Backup of json commands stored in {source_file} to {destination_file} complete.")

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

# TODO: Create migration script from json stored commands to database
def migrate_json_to_sqlite():
    pass