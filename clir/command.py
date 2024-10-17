import os
import re
import json
import uuid
import platform
import subprocess
from datetime import datetime
from rich import box
from rich import print
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from clir.utils.config import verify_xclip_installation
from clir.utils.core import get_commands, replace_arguments, transform_commands_to_json
from clir.utils.db import insert_command_db, get_commands_db, remove_command_db, verify_command_id_exists, verify_command_id_tag_relation_exists, modify_command_db

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
        current_commands = get_commands_db()

        command = self.command
        desc = self.description
        tag = self.tag

        if not tag:
            tag = "clir"

        insert_command_db(command, desc, tag)

        print(f'Command saved successfuly')


#Create class Table
class CommandTable:
    def __init__(self, tag: str = "", grep: str = ""):
        self.commands = transform_commands_to_json(get_commands_db(tag = tag, grep = grep))
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
        
        command = replace_arguments(command)
        if uid and command:
            print(f'[bold green]Running command:[/bold green] {command}')
            os.system(command)
            subprocess.Popen(['bash', '-ic', 'set -o history; history -s "$1"', '_', command])
    
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
                if verify_xclip_installation(package = "pbcopy"):
                    os.system(f'printf "{command}" | pbcopy')
                else:
                    print("pbcopy is not installed, this command needs pbcopy to work properly")
                    return
            elif platform.system() == "Linux":
                # Verify that xclip is installed
                if verify_xclip_installation(package = "xclip"):
                    os.system(f'echo -n "{command}" | xclip -selection clipboard')
                else:
                    print("xclip is not installed, this command needs xclip to work properly")
                    return
            else:
                print("OS not supported")
    
    def show_tags(self):
        current_commands = self.commands

        tags = []
        for command in current_commands:
            tags.append(current_commands[command]["tag"])
        
        tags = list(dict.fromkeys(tags))

        table = Table(show_lines=True, box=box.ROUNDED, style="grey46")
        table.add_column("Tags 🏷️", style="cyan bold")
        
        for tag in tags:
            table.add_row(tag)

        console = Console()
        console.print(table)
        print(f"Showing {str(len(tags))} tags")

    def export_commands(self):
        try:
            with open("commands.json", "w") as commands_file:
                json.dump(self.commands, commands_file)
            print(f"[bold green]Commands exported succesfully[/bold green] to {os.getcwd()}/commands.json")
        except:
            print("[bold red]Commands could not be exported[/bold red]")
            raise
    
    def import_commands(self, import_file_path: str = ""):
        if import_file_path:
            import_commands = ""
            existing_commands = self.commands


            if os.path.exists(import_file_path):
                try:
                    with open(import_file_path, 'r') as import_file:
                        print(f"Importing commands from {import_file_path}...")
                        import_commands =  json.load(import_file)
                except Exception as e:
                    raise Exception(f"Un error ocurred while reading the file '{import_file_path}'")
            else:
                raise FileNotFoundError(f"File '{import_file_path}' could not be found")


            for command, data in import_commands.items():
                if command in existing_commands.keys() \
                and data['description'] == existing_commands[command]["description"] \
                and data['tag'] == existing_commands[command]["tag"]:
                    print(f"No changes detected in command [bold green]{command}[/bold green]. Command not imported.")
                    print("---")

                elif command in existing_commands.keys() \
                and (data['description'] != existing_commands[command]["description"] or data['tag'] != existing_commands[command]["tag"]):
                    import_choice = ""
                    print("The command [bold green]{command}[/bold green] already exists in the database:")
                    print(data)
                    table = Table(show_lines=True, box=box.ROUNDED, style="grey46")
                    table.add_column("", style="white bold", no_wrap=True)
                    table.add_column("Import", style="green bold", no_wrap=True)
                    table.add_column("Database", style="magenta bold")
                    table.add_row("Command", command, command)
                    table.add_row("Description", data['description'], existing_commands[command]["description"])
                    table.add_row("Tag", data['tag'], existing_commands[command]["tag"])
                    table.add_row("Creation date", data['creation_date'], existing_commands[command]["creation_date"])
                    table.add_row("Laste modification date", data['last_modif_date'], existing_commands[command]["last_modif_date"])
                    console = Console()
                    console.print(table)

                    while import_choice != "n" and import_choice != "y":
                        import_choice = Prompt.ask("Do you want to replace the existing command? (y/n)").lower()

                    if import_choice == "y":
                        print(f"Importing command: {command}")
                        print(f"Description: {data['description']}")
                        print(f"Tag: {data['tag']}")
                        print(f"Creation date: {data['creation_date']}")
                        print(f"Last modification date: {data['last_modif_date']}")
                        modify_command_db(command, data['description'], data['tag'], data['creation_date'], data['last_modif_date'])
                        print("---")
                    elif import_choice == "n":
                        print("Keeping the already existing command.")
                
                else:
                    print(f"Importing command: {command}")
                    print(f"Description: {data['description']}")
                    print(f"Tag: {data['tag']}")
                    print(f"Creation date: {data['creation_date']}")
                    print(f"Last modification date: {data['last_modif_date']}")
                    insert_command_db(command, data['description'], data['tag'], data['creation_date'], data['last_modif_date'])
                    print("---")

            print("Import complete")
        else:
            print("No file was passed to import")

    # Create a function that deletes a command when passing its uid
    def remove_command(self):

        uid = self.get_command_uid()

        remove_command_db(uid)
        verify_command_id_exists(uid)
        verify_command_id_tag_relation_exists(uid)

        if verify_command_id_exists(uid):
            print(f'Command not removed')
        elif not verify_command_id_exists(uid) and verify_command_id_tag_relation_exists(uid):
            print(f'Command removed successfuly but relation to tag not removed')
        elif not verify_command_id_exists(uid) and not verify_command_id_tag_relation_exists(uid):
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