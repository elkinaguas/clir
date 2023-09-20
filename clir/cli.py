import click
import os
from rich.prompt import Prompt
from clir.tools import functions

@click.group()
def cli():
    pass

#--------------------------------------- CLI commands  -------------------------------------------------------

@cli.command(help="Clir initial configuration")
def init():
    dir_path = os.path.join(os.path.expanduser('~'), '.clir')
    os.makedirs(dir_path, exist_ok=True)
    
    # Define the file path and name
    file_path = os.path.join(dir_path, 'commands.json')

    # Check if the file already exists
    if not os.path.exists(file_path):
        # Create the file
        with open(file_path, 'w') as file:
            file.write('{}')

        print(f'File "{file_path}" created successfully.')
    else:
        print(f'A clir environment already exists in "{dir_path}".')

@cli.command(help="Save new command")
def new():
    command = Prompt.ask("Command")
    description = Prompt.ask("Description")
    tag = Prompt.ask("Tag")

    functions.save_commands(command = command, desc = description, tag = tag)

@cli.command(help="Remove command")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def rm(tag: str = "", grep: str = ""):
    if tag or grep:
        commands = functions.search_command(tag=tag, grep=grep)
    else:
        commands = functions.get_commands()
    uid = functions.choose_command(commands=commands)
    functions.remove_command(uid = uid)

@cli.command(help="List commands")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def ls(tag: str = "", grep: str = ""):
    if tag or grep:
        commands = functions.search_command(tag=tag, grep=grep)
    else:
        commands = functions.get_commands()
    functions.command_table(commands=commands)

@cli.command(help="Run command")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def run(tag: str = "", grep: str = ""):
    if tag or grep:
        commands = functions.search_command(tag=tag, grep=grep)
    else:
        commands = functions.get_commands()
    uid = functions.choose_command(commands=commands)
    functions.run_command(uid = uid)

