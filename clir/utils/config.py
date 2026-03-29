import importlib.resources
import json
import shutil
from pathlib import Path

from clir.utils.core import get_commands
from clir.utils.db import create_database, create_local_database, find_local_db, insert_command_db, set_active_db

config_directory = "clir/config/"


def _env_path() -> Path:
    return Path.home() / ".clir"


def _commands_json_path() -> Path:
    return _env_path() / "commands.json"


def _config_file_path() -> Path:
    return _env_path() / "clir.conf"


def _db_file_path() -> Path:
    return _env_path() / "clir.db"

def check_config():
    return _db_file_path().exists() and _config_file_path().exists()

def back_json_commands():
    source_file = _commands_json_path()
    destination_file = _env_path() / "commands.json.backup"

    shutil.copyfile(source_file, destination_file)

    print(f"Backup of json commands stored in {source_file} to {destination_file} complete.")

def migrate_json_to_sqlite():
    commands_json_path = _commands_json_path()

    if commands_json_path.exists():
        back_json_commands()
        print("Migrating json stored commands to sqlite database...")
        
        commands = get_commands()

        for command, data in commands.items():
            print(f"Inserting command: {command}")
            print(f"Description: {data['description']}")
            print(f"Tag: {data['tag']}")
            insert_command_db(command, data['description'], data['tag'])
            print("---")

        commands_json_path.unlink()
        print("Migration complete")


def create_config_files():
    dir_path = _env_path()
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # Define the file path and name
    files = ['commands.json']

    # Check if the file already exists
    for file in files:
        file_path = dir_path / file
        if not file_path.exists():
            # Create the file
            with open(file_path, 'w') as file_object:
                file_object.write('{}')

            print(f'File "{file_path}" created successfully.')
        else:
            print(f'A clir environment already exists in "{dir_path}".')

def copy_config_files():
    dir_path = _env_path()
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # Define the file path and name
    files = ['clir.conf']

    # Check if the file already exists
    for file_name in files:
        with importlib.resources.open_text('clir.config', 'clir.conf') as f:
            conf = f.read()
            with open(dir_path / file_name, "w") as file_object:
                file_object.write(conf)

        print(f"Copying {file_name} file to {dir_path}")

def init_config():
    if not check_config():
        dir_path = _env_path()
        dir_path.mkdir(parents=True, exist_ok=True)

        print("Setting up initial configuration")
        print("Creating database...")
        create_database()
        print("Database created successfully")

        print("Creating config files...")
        create_config_files()

        print("Copying other config files...")
        copy_config_files()

        migrate_json_to_sqlite()
    
    if not check_config():
        print("Could not set the initial configuration Up.")
        return
    

def verify_clipboard_tool_installation(package: str = ""):
    if package in {"xclip", "pbcopy"}:
        return shutil.which(package) is not None

    return False


def read_setting(name: str):
    config_path = _config_file_path()
    if not config_path.exists():
        return None
    with open(config_path) as f:
        config = json.load(f)
    for setting in config.get("settings", []):
        if setting["name"] == name:
            return setting["value"]
    return None


def write_setting(name: str, value) -> bool:
    config_path = _config_file_path()
    if not config_path.exists():
        return False
    with open(config_path) as f:
        config = json.load(f)
    for setting in config.get("settings", []):
        if setting["name"] == name:
            setting["value"] = value
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            return True
    return False


def init_local_config(directory: Path = None) -> Path:
    if directory is None:
        directory = Path.cwd()
    return create_local_database(directory)


def configure_active_db(local: bool = False, use_global: bool = False) -> None:
    set_active_db(None)  # reset to global each invocation

    if use_global:
        return

    if local:
        db_path = find_local_db()
        if db_path is None:
            raise ValueError(
                "No local clir project found. Run 'clir init' in your project directory first."
            )
        set_active_db(db_path)
        print(f"[local: {db_path.parent}]")
        return

    if read_setting("default_current_folder"):
        db_path = find_local_db()
        if db_path:
            set_active_db(db_path)
            print(f"[local: {db_path.parent}]")
