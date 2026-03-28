# clir
[![PyPI](https://img.shields.io/pypi/v/clir)](https://pypi.org/project/clir/) ![PyPI - Downloads](https://img.shields.io/pypi/dm/clir) ![Total Download](https://static.pepy.tech/badge/clir)

Clir provides a clear and fast way to store and recover your commands.

## What's new in 0.9.0
- Bulk remove supports comma-separated IDs and ranges (for example `1,3-5`).
- Remove flow supports `all` to delete all commands shown in the filtered table.
- Remove confirmation now includes the command name for each deleted command.
- Test suite and CI coverage were expanded with new branch and integration tests.

## Installation
`clir` supports Python 3.9+.

Recommended:

```bash
pipx install clir
```

Alternative:

```bash
pip install clir
```

## Usage
`clir` initializes automatically the first time you run a real command.

See all the options available with
```bash
clir --help
```
![clir --help](https://raw.githubusercontent.com/elkinaguas/clir/main/docs/img/clir_help.png)

List your saved commands:
```bash
clir ls
```
![clir ls](https://raw.githubusercontent.com/elkinaguas/clir/main/docs/img/clir_ls.png)
