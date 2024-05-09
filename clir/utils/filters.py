import re
import clir.utils.core as core

def filter_by_tag(commands: dict = {}, tag: str = ""):
    if commands:
        current_commands = commands
    else:
        current_commands = core.get_commands()

    tag_commands = {}
    for command in current_commands:
        if current_commands[command]["tag"] == tag:
            tag_commands[command] = current_commands[command]

    return tag_commands

def filter_by_grep(commands: dict = {}, grep: str = ""):
    if commands:
        current_commands = commands
    else:
        current_commands = core.get_commands()

    grep_commands = {}
    pattern = grep
    for command in current_commands:
        text = command + " " + current_commands[command]["description"]# + " " + current_commands[command]["tag"]
        match = re.findall(pattern, text, re.IGNORECASE)
        if match:
            grep_commands[command] = current_commands[command]

    return grep_commands