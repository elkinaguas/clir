import os
import json
from rich.prompt import Prompt
from clir.cli import rm
from click.testing import CliRunner


file_path = os.path.expanduser('~/.clir/commands.json')
current_commands = {}

def get_current_commands():
    with open(file_path, 'r') as file:
        current_commands = json.load(file)
        for command in current_commands:
            current_commands[command]["uid"] = ""
    
    return current_commands

# Test delete command
def test_delete_command():
    expected_commands = {"command 2":
                         {"description": "Command 2 description", "tag": "c2", "uid": ""}}
    runner = CliRunner()
    result = runner.invoke(rm, input='1\n')
    assert result.exit_code == 0
    assert str(get_current_commands()) == str(expected_commands)



