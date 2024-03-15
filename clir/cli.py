import rich_click as click
import os
import subprocess
from rich.prompt import Prompt
from clir.command import Command
from clir.command import CommandTable

@click.group()
def cli():
    pass

def check_config():
    dir_path = os.path.join(os.path.expanduser('~'), '.clir')
    file_path = os.path.join(dir_path, 'commands.json')

    return os.path.exists(file_path)

#--------------------------------------- CLI commands  -------------------------------------------------------

@cli.command(help="Clir initial configuration 🛠️")
def init():
    dir_path = os.path.join(os.path.expanduser('~'), '.clir')
    os.makedirs(dir_path, exist_ok=True)
    
    # Define the file path and name
    files = ['commands.json', 'credentials.json']

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

@cli.command(help="Save new command 💾")
@click.option('-c', '--command', help="Command to be saved", prompt=True)
@click.option('-d', '--description', help="Description of the command", prompt=True)
@click.option('-t', '--tag', help="Tag to be associated with the command", prompt=True)
def new(command, description, tag):
    if not check_config():
        print("Initial configuration is not set. Executing 'clir init'...")
        subprocess.run(["clir", "init"])

    # Check again after executing 'clir init'
    if not check_config():
        print("Could not set the initial configuration. Unable to add the new command.")
        return
    
    new_command = Command(command = command, description = description, tag = tag)
    new_command.save_command()

@cli.command(help="Remove command 👋")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def rm(tag: str = "", grep: str = ""):
    table = CommandTable(tag=tag, grep=grep)
    table.remove_command()

@cli.command(help="List commands 📃")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def ls(tag: str = "", grep: str = ""):
    table = CommandTable(tag=tag, grep=grep)
    table.show_table()

@cli.command(help="Run command 🚀")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def run(tag: str = "", grep: str = ""):
    table = CommandTable(tag=tag, grep=grep)
    table.run_command()

@cli.command(help="Copy command to clipboard 📋")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def cp(tag: str = "", grep: str = ""):
    table = CommandTable(tag=tag, grep=grep)
    table.copy_command()

@cli.command(help="Show tags 🏷️")
@click.option('-g', '--grep', help="Search by grep")
def tags(grep: str = ""):
    table = CommandTable(grep=grep)
    table.show_tags()