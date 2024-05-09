import os
import re
import json
import clir.utils.filters as filters

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

def get_user_input(arg):
    return input(f"Enter value for '{arg}': ")

def replace_arguments(command):
    # Use regex to find all arguments with underscores
    matches = re.findall(r'_\w+', command)

    # Check that all arguments are unique
    if len(matches) != len(set(matches)):
        print("[bold red]Make sure that all arguments are unique[/bold red]")
        return None
    
    # Prompt the user for values for each argument
    replacements = {arg: get_user_input(arg) for arg in matches}
    
    # Split the command into a list
    command_list = command.split(" ")

    # Replace arguments in the command
    for arg, value in replacements.items():
        for indx,term in enumerate(command_list):
            if arg == term:
                command_list[indx] = value
    
    return " ".join(command_list)