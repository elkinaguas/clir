import rich_click as click
import os
import subprocess
from rich.prompt import Prompt
from clir.command import Command
from clir.command import CommandTable
from clir.utils.config import init_config

@click.group()
def cli():
    pass



@cli.command(help="Save new command 💾")
@click.option('-c', '--command', help="Command to be saved", prompt=True)
@click.option('-d', '--description', help="Description of the command", prompt=True)
@click.option('-t', '--tag', help="Tag to be associated with the command", prompt=True)
def new(command, description, tag):
    init_config()
    new_command = Command(command = command, description = description, tag = tag)
    new_command.save_command()

@cli.command(help="Remove command 👋")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def rm(tag: str = "", grep: str = ""):
    init_config()
    table = CommandTable(tag=tag, grep=grep)
    table.remove_command()

@cli.command(help="List commands 📃")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def ls(tag: str = "", grep: str = ""):
    init_config()    
    table = CommandTable(tag=tag, grep=grep)
    table.show_table()

@cli.command(help="Run command 🚀")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def run(tag: str = "", grep: str = ""):
    init_config()
    table = CommandTable(tag=tag, grep=grep)
    table.run_command()

@cli.command(help="Copy command to clipboard 📋")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def cp(tag: str = "", grep: str = ""):
    init_config()
    table = CommandTable(tag=tag, grep=grep)
    table.copy_command()

@cli.command(help="Show tags 🏷️")
@click.option('-g', '--grep', help="Search by grep")
def tags(grep: str = ""):
    init_config()
    table = CommandTable(grep=grep)
    table.show_tags()

@cli.command(help="Import commands from file 🤓")
@click.option('-f', '--file', help="Search by grep")
def imports(file: str = ""):
    init_config()
    if file:
        table = CommandTable()
        table.import_commands(import_file_path = file)
    else:
        while not file:
            file = str(Prompt.ask("Insert import file path"))
        table = CommandTable()
        table.import_commands(import_file_path = file)

@cli.command(help="Export commands to file 📤")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def export(tag: str = "", grep: str = ""):
    init_config()
    table = CommandTable(tag=tag, grep=grep)
    table.export_commands()