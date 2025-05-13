import os
import re
import json
import clir.utils.filters as filters
from clir.utils.db import get_tag_id_from_command_id, get_tag_from_tag_id

# Create a function that returns all commands
def get_commands(tag: str = "", grep: str = ""):
    current_commands = ""
    json_file_path = os.path.join(os.path.expanduser('~'), '.clir/commands.json')

    try:
        with open(json_file_path, 'r') as json_file:
            current_commands =  json.load(json_file)
    except FileNotFoundError:
        return []
    
    if tag:
        current_commands = filters.filter_by_tag(commands=current_commands, tag=tag)
    if grep:
        current_commands = filters.filter_by_grep(commands=current_commands, grep=grep)
    
    sorted_commands = dict(sorted(current_commands.items(), key=lambda item: item[1]["tag"]))

    return sorted_commands

def transform_commands_to_json(commands):
    commands_json = {}
    
    for command in commands:
        commands_json[command[3]] = {
            "description": command[4],
            "tag": get_tag_from_tag_id(get_tag_id_from_command_id(command[0])),
            "uid": command[0],
            "creation_date": command[1],
            "last_modif_date": command[2]
        }
    
    return commands_json


def get_user_input(arg):
    return input(f"Enter value for '{arg}': ")

def replace_arguments(command):
    # Use regex to find all arguments with @ prefix that have a space before them
    # This avoids matching email addresses or other @ uses
    matches = re.findall(r'(?<=\s)@[\w-]+(?!\S*@)', command)
    
    # Create a dict to store unique variables and their values
    replacements = {}
    
    # Get user input only once for each unique variable
    for var in matches:
        if var not in replacements:
            replacements[var] = get_user_input(var)
    
    # Replace all occurrences of each variable in the command
    for var, value in replacements.items():
        command = command.replace(var, value)
    
    return command

def uuid_to_base64(uuid_obj):
    uuid_bytes = uuid_obj.bytes
    base64_uuid = base64.urlsafe_b64encode(uuid_bytes).rstrip(b'=').decode('ascii')
    return base64_uuid

def base64_to_uuid(base64_uuid):
    padding = '=' * (4 - len(base64_uuid) % 4)  # Add padding if necessary
    uuid_bytes = base64.urlsafe_b64decode(base64_uuid + padding)
    return uuid.UUID(bytes=uuid_bytes)
