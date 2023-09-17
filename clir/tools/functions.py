import os
import re
import json
import uuid
from rich import box
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt


def get_commands():
    current_commands = ""
    json_file_path = os.path.join(os.path.expanduser('~'), '.clir/commands.json')

    try:
        with open(json_file_path, 'r') as json_file:
            current_commands =  json.load(json_file)
    except FileNotFoundError:
        return []
    
    return current_commands

def choose_command(commands: dict = {}):
    command_table(commands=commands)
    command_id = Prompt.ask("Enter command ID")

    try:
        while int(command_id) > len(commands) or int(command_id) < 1:
            print("ID not valid")
            command_id = Prompt.ask("Enter command ID")
        
        command = commands[list(commands.keys())[int(command_id)-1]]["uid"]

        return command
    except ValueError:
        print("ID must be an integer")
    
    return ""


def command_table(commands: dict = {}):
    current_commands = commands
    
    table = Table(show_lines=True, box=box.MINIMAL)

    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="magenta")
    table.add_column("Tag", style="green")
    
    for indx, command in enumerate(current_commands):
        table.add_row(str(indx+1), command, current_commands[command]["description"], current_commands[command]["tag"])

    console = Console()
    console.print(table)

def save_commands(command: str = "", desc: str = "", tag: str = ""):
    current_commands = get_commands()
    json_file_path = os.path.join(os.path.expanduser('~'), '.clir/commands.json')

    uid = uuid.uuid4()
    
    current_commands[str(command)] = {"description": desc, "tag": tag, "uid": str(uid)}

    # Write updated data to JSON file
    with open(json_file_path, 'w') as json_file:
        json.dump(current_commands, json_file)

    print(f'Command saved successfuly')

# Create a function that deletes a command when passing its uid
def remove_command(uid: str = ""):
    current_commands = get_commands()
    json_file_path = os.path.join(os.path.expanduser('~'), '.clir/commands.json')
    
    del_command = ""
    for command in current_commands:
        if current_commands[command]["uid"] == uid:
            del_command = command
    
    if uid:
        current_commands.pop(str(del_command))

        # Write updated data to JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(current_commands, json_file)

        print(f'Command removed successfuly')

def run_command(uid: str = ""):
    current_commands = get_commands()
    
    command = ""
    for c in current_commands:
        if current_commands[c]["uid"] == uid:
            command = c
    
    if uid:
        print(f'Running command: {command}')
        os.system(command)


def _filter_by_tag(commands: dict = {}, tag: str = ""):
    if commands:
        current_commands = commands
    else:
        current_commands = get_commands()

    tag_commands = {}
    for command in current_commands:
        if current_commands[command]["tag"] == tag:
            tag_commands[command] = current_commands[command]

    return tag_commands

def _filter_by_grep(commands: dict = {}, grep: str = ""):
    if commands:
        current_commands = commands
    else:
        current_commands = get_commands()

    grep_commands = {}
    pattern = grep
    for command in current_commands:
        text = command + " " + current_commands[command]["description"]# + " " + current_commands[command]["tag"]
        match = re.findall(pattern, text, re.IGNORECASE)
        if match:
            grep_commands[command] = current_commands[command]

    return grep_commands

# Create a function that searches for a command by tag
def search_command(tag: str = "", grep: str = ""):
    filtered_commands = {}
    if grep:
        grep_commands = _filter_by_grep(commands=filtered_commands, grep=grep)
        filtered_commands = grep_commands
    if tag:
        tag_commands = _filter_by_tag(commands=filtered_commands, tag=tag)
        filtered_commands = tag_commands

    return filtered_commands