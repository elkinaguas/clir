import os
import shutil
import subprocess
from pathlib import Path
from clir.utils.db import create_database
from clir.utils.core import get_commands
from clir.utils.db import insert_command_db
import importlib.resources

config_directory = "clir/config/"
env_path = Path('~').expanduser() / Path(".clir")

def check_config():
    dir_path = os.path.join(os.path.expanduser('~'), '.clir')
    db_file_path = os.path.join(dir_path, 'clir.db')
    config_file_path = os.path.join(dir_path, 'clir.conf')

    return os.path.exists(db_file_path) and os.path.exists(config_file_path)

def back_json_commands():
    source_file = f"{env_path}/commands.json"
    destination_file = f"{env_path}/commands.json.backup"

    shutil.copyfile(source_file, destination_file)

    print(f"Backup of json commands stored in {source_file} to {destination_file} complete.")

def migrate_json_to_sqlite():
    if os.path.exists(f"{env_path}/commands.json"):
        back_json_commands()
        print("Migrating json stored commands to sqlite database...")
        
        commands = get_commands()

        for command, data in commands.items():
            print(f"Inserting command: {command}")
            print(f"Description: {data['description']}")
            print(f"Tag: {data['tag']}")
            insert_command_db(command, data['description'], data['tag'])
            print("---")

        os.remove(f"{env_path}/commands.json")
        print("Migration complete")


def create_config_files():
    dir_path = os.path.join(os.path.expanduser('~'), '.clir')
    os.makedirs(dir_path, exist_ok=True)
    
    # Define the file path and name
    files = ['commands.json']

    # Check if the file already exists
    for file in files:
        file_path = os.path.join(dir_path, file)
        if not os.path.exists(file_path):
            # Create the file
            with open(file_path, 'w') as file_object:
                file_object.write('{}')

            print(f'File "{file_path}" created successfully.')
        else:
            print(f'A clir environment already exists in "{dir_path}".')

def copy_config_files():
    dir_path = os.path.join(os.path.expanduser('~'), '.clir')
    os.makedirs(dir_path, exist_ok=True)
    
    # Define the file path and name
    files = ['clir.conf']

    # Check if the file already exists
    for file in files:
        with importlib.resources.open_text('clir.config', 'clir.conf') as f:
            conf = f.read()
            with open(f"{env_path}/{file}", "w") as file:
                file.write(conf)

        print(f"Copying {file} file to {env_path}")

def init_config():
    if not check_config():
        dir_path = os.path.join(os.path.expanduser('~'), '.clir')
        os.makedirs(dir_path, exist_ok=True)

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
    

def verify_xclip_installation(package: str = ""):
    if package == "xclip":
        try:
            subprocess.run(["xclip", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    if package == "pbcopy":
        try:
            subprocess.run(["which", "pbcopy"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    
    return "No package specified"