import os
import json
from rich.prompt import Prompt
from clir.cli import new
from click.testing import CliRunner


file_path = os.path.expanduser('~/.clir/commands.json')
current_commands = {}

def get_current_commands():
    with open(file_path, 'r') as file:
        current_commands = json.load(file)
        for command in current_commands:
            current_commands[command]["uid"] = ""
    
    return current_commands

# Test add new command using flags
def test_add_new_command():
    expected_commands = {"command 1": {"description": "Command 1 description", "tag": "c1", "uid": ""}}
    runner = CliRunner()
    result = runner.invoke(new, ['-c', "command 1", '-d', "Command 1 description", '-t', "c1"])
    assert result.exit_code == 0
    assert str(get_current_commands()) == str(expected_commands)

# Test add new command using prompts
def test_add_new_command_with_prompt():
    expected_commands = {"command 1": 
                         {"description": "Command 1 description", "tag": "c1", "uid": ""},
                         "command 2":
                         {"description": "Command 2 description", "tag": "c2", "uid": ""}}
    runner = CliRunner()
    result = runner.invoke(new, input='\n'.join(["command 2", "Command 2 description", "c2"]))
    assert result.exit_code == 0
    assert str(get_current_commands()) == str(expected_commands)



