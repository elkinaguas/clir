import os
import re
import json
import uuid
import platform
import subprocess
from rich import box
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

class Command:
    def __init__(self, command: str = "", description: str = "", tag: str = ""):
        self.command = command
        self.description = description
        self.tag = tag
        self.uid = uuid.uuid4()

    def __str__(self):
        return f"{self.command} {self.description} {self.tag}"
    
    def __repr__(self):
        return f"{self.command} {self.description} {self.tag}"

    def save_command(self):
        current_commands = _get_commands()

        command = self.command
        desc = self.description
        tag = self.tag

        json_file_path = os.path.join(os.path.expanduser('~'), '.clir/commands.json')

        uid = uuid.uuid4()
        
        current_commands[str(command)] = {"description": desc, "tag": tag, "uid": str(uid)}

        # Write updated data to JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(current_commands, json_file)

        print(f'Command saved successfuly')


#Create class Table
class CommandTable:
    def __init__(self, tag: str = "", grep: str = ""):
        self.commands = _get_commands(tag = tag, grep = grep)
        self.tag = tag
        self.grep = grep

    def __str__(self):
        return f"{self.command} {self.description} {self.tag}"

    def __repr__(self):
        return f"{self.command} {self.description} {self.tag}"

    def show_table(self):

        commands = self.commands

        table = Table(show_lines=True, box=box.ROUNDED, style="grey46")
        table.add_column("ID 📇", style="white bold", no_wrap=True)
        table.add_column("Command 💻", style="green bold", no_wrap=True)
        table.add_column("Description 📕", style="magenta bold")
        table.add_column("Tag 🏷️", style="cyan bold")
        
        for indx, command in enumerate(commands):
            desc_len = 50
            command_len = 50
            description = commands[command]["description"]
            split_description = "\n".join([description[i:i+desc_len] for i in range(0, len(description), desc_len)])
            split_command = []
            local_command = ""
            for command_term in command.split(" "):
                if len(local_command) + len(command_term) > command_len:
                    split_command.append(local_command)
                    local_command = command_term + " "
                else:
                    local_command += command_term + " "
                
            split_command.append(local_command)
            
            display_command = " \ \n".join(split_command)
            table.add_row(str(indx+1), display_command, split_description, commands[command]["tag"])

        console = Console()
        console.print(table)
        print(f"Showing {str(len(commands))} commands")
    
    def run_command(self):
        current_commands = self.commands

        uid = self.get_command_uid()
        
        command = ""
        for c in current_commands:
            if current_commands[c]["uid"] == uid:
                command = c
        
        if uid:
            print(f'Running command: {command}')
            os.system(command)
    
    def copy_command(self):
        current_commands = self.commands

        uid = self.get_command_uid()
        
        command = ""
        for c in current_commands:
            if current_commands[c]["uid"] == uid:
                command = c
        
        if uid:
            print(f'Copying command: {command}')
            if platform.system() == "Darwin":
                # Verify that pbcopy is installed
                if _verify_installation(package = "pbcopy"):
                    os.system(f'echo -n "{command}" | pbcopy')
                else:
                    print("pbcopy is not installed, this command needs pbcopy to work properly")
                    return
            elif platform.system() == "Linux":
                # Verify that xclip is installed
                if _verify_installation(package = "xclip"):
                    os.system(f'echo -n "{command}" | xclip -selection clipboard')
                else:
                    print("xclip is not installed, this command needs xclip to work properly")
                    return
            else:
                print("OS not supported")

    # Create a function that deletes a command when passing its uid
    def remove_command(self):
        json_file_path = os.path.join(os.path.expanduser('~'), '.clir/commands.json')

        uid = self.get_command_uid()
        
        del_command = ""
        for command in self.commands:
            if self.commands[command]["uid"] == uid:
                del_command = command

        if uid:
            self.commands.pop(str(del_command))

            # Write updated data to JSON file
            with open(json_file_path, 'w') as json_file:
                json.dump(self.commands, json_file)

            print(f'Command removed successfuly')


    def get_command_uid(self):
        self.show_table()
        command_id = Prompt.ask("Enter command ID")

        try:
            while int(command_id) > len(self.commands) or int(command_id) < 1:
                print("ID not valid")
                command_id = Prompt.ask("Enter command ID")
            
            command = self.commands[list(self.commands.keys())[int(command_id)-1]]["uid"]

            return command
        except ValueError:
            print("ID must be an integer")
        
        return ""

def _verify_installation(package: str = ""):
    if package == "xclip":
        try:
            subprocess.run(["xclip", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    if package == "pbcopy":
        try:
            subprocess.run(["pbcopy", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    
    return "No package specified"

def _filter_by_tag(commands: dict = {}, tag: str = ""):
    if commands:
        current_commands = commands
    else:
        current_commands = _get_commands()

    tag_commands = {}
    for command in current_commands:
        if current_commands[command]["tag"] == tag:
            tag_commands[command] = current_commands[command]

    return tag_commands

def _filter_by_grep(commands: dict = {}, grep: str = ""):
    if commands:
        current_commands = commands
    else:
        current_commands = _get_commands()

    grep_commands = {}
    pattern = grep
    for command in current_commands:
        text = command + " " + current_commands[command]["description"]# + " " + current_commands[command]["tag"]
        match = re.findall(pattern, text, re.IGNORECASE)
        if match:
            grep_commands[command] = current_commands[command]

    return grep_commands

# Create a function that returns all commands
def _get_commands(tag: str = "", grep: str = ""):
    current_commands = ""
    json_file_path = os.path.join(os.path.expanduser('~'), '.clir/commands.json')

    try:
        with open(json_file_path, 'r') as json_file:
            current_commands =  json.load(json_file)
    except FileNotFoundError:
        return []
    
    if tag:
        current_commands = _filter_by_tag(commands=current_commands, tag=tag)
    if grep:
        current_commands = _filter_by_grep(commands=current_commands, grep=grep)
    
    sorted_commands = dict(sorted(current_commands.items(), key=lambda item: item[1]["tag"]))

    return sorted_commands