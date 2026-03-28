import rich_click as click
from rich.prompt import Prompt

from clir.command import Command
from clir.command import CommandTable
from clir.utils.config import init_config


@click.group()
def cli():
    pass


def _get_command_table(tag: str = "", grep: str = "", tag_grep: str = "") -> CommandTable:
    init_config()
    return CommandTable(tag=tag, grep=grep, tag_grep=tag_grep)


def _prompt_import_file(file_path: str = "") -> str:
    while not file_path:
        file_path = str(Prompt.ask("Insert import file path"))
    return file_path



@cli.command(help="Save new command 💾")
@click.option('-c', '--command', help="Command to be saved", prompt=True)
@click.option('-d', '--description', help="Description of the command", prompt=True)
@click.option('-t', '--tag', help="Tag to be associated with the command", prompt=True)
def new(command, description, tag):
    init_config()
    new_command = Command(command=command, description=description, tag=tag)
    new_command.save_command()

@cli.command(help="Remove command(s) 👋. In the prompt use 1,3-5 or all")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def rm(tag: str = "", grep: str = ""):
    _get_command_table(tag=tag, grep=grep).remove_command()

@cli.command(help="List commands 📃")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def ls(tag: str = "", grep: str = ""):
    _get_command_table(tag=tag, grep=grep).show_table()

@cli.command(help="Run command 🚀")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def run(tag: str = "", grep: str = ""):
    _get_command_table(tag=tag, grep=grep).run_command()

@cli.command(help="Copy command to clipboard 📋")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def cp(tag: str = "", grep: str = ""):
    _get_command_table(tag=tag, grep=grep).copy_command()

@cli.command(help="Show tags 🏷️")
@click.option('-g', '--grep', help="Search by grep")
def tags(grep: str = ""):
    _get_command_table(tag_grep=grep).show_tags()

@cli.command(help="Import commands from file 🤓")
@click.option('-f', '--file', help="Search by grep")
def imports(file: str = ""):
    init_config()
    CommandTable().import_commands(import_file_path=_prompt_import_file(file))

@cli.command(help="Export commands to file 📤")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
def export(tag: str = "", grep: str = ""):
    _get_command_table(tag=tag, grep=grep).export_commands()

@cli.command(help="Settings ⚙️")
def settings():
    init_config()
