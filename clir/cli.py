import rich_click as click
from pathlib import Path
from rich import box
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from clir.command import Command
from clir.command import CommandTable
from clir.utils.config import (
    configure_active_db,
    init_config,
    init_local_config,
    read_setting,
    write_setting,
)
from clir.utils.db import find_local_db, get_active_db_path


@click.group()
def cli():
    pass


def _get_command_table(tag: str = "", grep: str = "", tag_grep: str = "", use_local: bool = False, use_global: bool = False) -> CommandTable:
    init_config()
    _setup_db(use_local, use_global)
    return CommandTable(tag=tag, grep=grep, tag_grep=tag_grep)


def _prompt_import_file(file_path: str = "") -> str:
    while not file_path:
        file_path = str(Prompt.ask("Insert import file path"))
    return file_path


def _setup_db(use_local: bool, use_global: bool) -> None:
    try:
        configure_active_db(use_local, use_global)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


def _find_git_root() -> Path:
    home = Path.home()
    current = Path.cwd()
    while True:
        if (current / ".git").exists():
            return current
        if current == home:
            break
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


@cli.command(help="Initialize local project DB 📁")
def init():
    init_config()

    local_db = Path.cwd() / ".clir" / "clir.db"
    if local_db.exists():
        print(f"Local clir project already initialized at [bold]{local_db.parent}[/bold]")
        return

    init_local_config(Path.cwd())
    print(f"[bold green]Local clir project initialized[/bold green] at {local_db}")

    git_root = _find_git_root()
    if git_root:
        gitignore = git_root / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            if ".clir" not in content:
                add = Prompt.ask("Add .clir/ to .gitignore?", choices=["y", "n"], default="y")
                if add == "y":
                    with open(gitignore, "a") as f:
                        f.write("\n# clir local project\n.clir/\n")
                    print(f"Added [bold].clir/[/bold] to {gitignore}")
        else:
            create = Prompt.ask(f"No .gitignore found at {git_root}. Create one with .clir/?", choices=["y", "n"], default="y")
            if create == "y":
                with open(gitignore, "w") as f:
                    f.write("# clir local project\n.clir/\n")
                print(f"Created {gitignore} with [bold].clir/[/bold]")


@cli.command(help="Save new command 💾")
@click.option('-c', '--command', help="Command to be saved", prompt=True)
@click.option('-d', '--description', help="Description of the command", prompt=True)
@click.option('-t', '--tag', help="Tag to be associated with the command", prompt=True)
@click.option('-l', '--local', 'use_local', is_flag=True, help="Use local project DB")
@click.option('-G', '--global', 'use_global', is_flag=True, help="Force global DB")
def new(command, description, tag, use_local, use_global):
    init_config()
    _setup_db(use_local, use_global)
    new_command = Command(command=command, description=description, tag=tag)
    new_command.save_command()


@cli.command(help="Remove command(s) 👋. In the prompt use 1,3-5 or all")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
@click.option('-l', '--local', 'use_local', is_flag=True, help="Use local project DB")
@click.option('-G', '--global', 'use_global', is_flag=True, help="Force global DB")
def rm(tag: str = "", grep: str = "", use_local: bool = False, use_global: bool = False):
    _get_command_table(tag=tag, grep=grep, use_local=use_local, use_global=use_global).remove_command()


@cli.command(help="List commands 📃")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
@click.option('-l', '--local', 'use_local', is_flag=True, help="Use local project DB")
@click.option('-G', '--global', 'use_global', is_flag=True, help="Force global DB")
def ls(tag: str = "", grep: str = "", use_local: bool = False, use_global: bool = False):
    _get_command_table(tag=tag, grep=grep, use_local=use_local, use_global=use_global).show_table()


@cli.command(help="Run command 🚀")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
@click.option('-l', '--local', 'use_local', is_flag=True, help="Use local project DB")
@click.option('-G', '--global', 'use_global', is_flag=True, help="Force global DB")
def run(tag: str = "", grep: str = "", use_local: bool = False, use_global: bool = False):
    _get_command_table(tag=tag, grep=grep, use_local=use_local, use_global=use_global).run_command()


@cli.command(help="Copy command to clipboard 📋")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
@click.option('-l', '--local', 'use_local', is_flag=True, help="Use local project DB")
@click.option('-G', '--global', 'use_global', is_flag=True, help="Force global DB")
def cp(tag: str = "", grep: str = "", use_local: bool = False, use_global: bool = False):
    _get_command_table(tag=tag, grep=grep, use_local=use_local, use_global=use_global).copy_command()


@cli.command(help="Show tags 🏷️")
@click.option('-g', '--grep', help="Search by grep")
@click.option('-l', '--local', 'use_local', is_flag=True, help="Use local project DB")
@click.option('-G', '--global', 'use_global', is_flag=True, help="Force global DB")
def tags(grep: str = "", use_local: bool = False, use_global: bool = False):
    _get_command_table(tag_grep=grep, use_local=use_local, use_global=use_global).show_tags()


@cli.command(help="Import commands from file 🤓")
@click.option('-f', '--file', help="Import file path")
@click.option('-l', '--local', 'use_local', is_flag=True, help="Use local project DB")
@click.option('-G', '--global', 'use_global', is_flag=True, help="Force global DB")
def imports(file: str = "", use_local: bool = False, use_global: bool = False):
    init_config()
    _setup_db(use_local, use_global)
    try:
        CommandTable().import_commands(import_file_path=_prompt_import_file(file))
    except (FileNotFoundError, ValueError) as exc:
        raise click.ClickException(str(exc)) from exc


@cli.command(help="Export commands to file 📤")
@click.option('-t', '--tag', help="Search by tag")
@click.option('-g', '--grep', help="Search by grep")
@click.option('-l', '--local', 'use_local', is_flag=True, help="Use local project DB")
@click.option('-G', '--global', 'use_global', is_flag=True, help="Force global DB")
def export(tag: str = "", grep: str = "", use_local: bool = False, use_global: bool = False):
    _get_command_table(tag=tag, grep=grep, use_local=use_local, use_global=use_global).export_commands()


@cli.command(help="Settings ⚙️")
@click.option('--default-local/--no-default-local', default=None, help="Always use local DB when available")
def settings(default_local):
    init_config()

    if default_local is not None:
        write_setting("default_current_folder", default_local)
        state = "enabled" if default_local else "disabled"
        print(f"Setting [bold cyan]default_current_folder[/bold cyan] {state}.")
        return

    active_db = get_active_db_path()
    home_db = Path.home() / ".clir" / "clir.db"
    is_local = active_db != home_db
    scope = "local" if is_local else "global"
    default_local_value = read_setting("default_current_folder") or False

    table = Table(show_lines=True, box=box.ROUNDED, style="grey46")
    table.add_column("Setting", style="cyan bold", no_wrap=True)
    table.add_column("Value", style="white bold")
    table.add_row("Active DB", f"{active_db} ({scope})")
    table.add_row("default_current_folder", str(default_local_value))

    console = Console()
    console.print(table)
