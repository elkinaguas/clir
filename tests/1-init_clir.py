import os
import subprocess, json
from clir.cli import ls
from click.testing import CliRunner
from clir.utils.db import DbIntegrity

dir_path = os.path.expanduser('~/.clir')
db_path = os.path.expanduser('~/.clir/clir.db')

def setup():
    os.makedirs(dir_path, exist_ok=True)
    subprocess.run(["cp", "tests/files/commands.json", f"{dir_path}/commands.json"])

# Test if the clir folder environment was created
def test_clir_project_folder_created():
    setup()
    runner = CliRunner()
    runner.invoke(ls)
    assert os.path.exists(dir_path)

# Test if the commands.json file was created
def test_command_db_created():
    assert os.path.exists(db_path)


def test_migration_files():
    assert not os.path.exists(os.path.expanduser('~/.clir/commands.json'))
    assert os.path.exists(os.path.expanduser('~/.clir/commands.json.backup'))

def test_migration():
    json_commands_len, json_commands, json_tags, _ = read_commands_json()
    cids, commands, tids, tags, crel, trel = db_integrity_check()
    assert json_commands_len == len(commands)
    assert set(json_commands) == set(commands)
    assert set(json_tags) == set(tags)
    assert len(crel) == json_commands_len
    assert len(trel) == json_commands_len

def read_commands_json():
    commands_json = {}
    commands = []
    tags = []
    description = []

    # Read commands.json file and load it in a dictionary
    with open(f"{dir_path}/commands.json.backup", 'r') as file:
        commands_json = json.load(file)
    
    counter = 1
    for command, data in commands_json.items():
        commands.append(command)
        tags.append(data['tag'])
        description.append(data['description'])
    
    return len(commands), commands, tags, description

def db_integrity_check():
    db_integrity = DbIntegrity()
    #commands_ids, commands, tags_ids, tags, cid_relation (commands ids in commands_tags table), tid_relation (commands ids in commands_tags table)
    return db_integrity.main()