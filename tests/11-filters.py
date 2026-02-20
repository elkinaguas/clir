import clir.utils.filters as filters


def test_filter_by_tag_uses_passed_commands_dict():
    commands = {
        "echo one": {"tag": "ops", "description": "first"},
        "echo two": {"tag": "dev", "description": "second"},
        "echo three": {"tag": "ops", "description": "third"},
    }

    result = filters.filter_by_tag(commands=commands, tag="ops")

    assert list(result.keys()) == ["echo one", "echo three"]


def test_filter_by_tag_loads_from_core_when_commands_missing(monkeypatch):
    monkeypatch.setattr(
        filters.core,
        "get_commands",
        lambda: {"echo one": {"tag": "ops", "description": "first"}},
    )

    result = filters.filter_by_tag(tag="ops")

    assert result == {"echo one": {"tag": "ops", "description": "first"}}


def test_filter_by_grep_matches_command_and_description_case_insensitive():
    commands = {
        "kubectl get pods": {"tag": "k8s", "description": "List Pods"},
        "terraform plan": {"tag": "tf", "description": "Preview changes"},
        "docker ps": {"tag": "docker", "description": "List containers"},
    }

    result = filters.filter_by_grep(commands=commands, grep="pods|preview")

    assert set(result.keys()) == {"kubectl get pods", "terraform plan"}


def test_filter_by_grep_loads_from_core_when_commands_missing(monkeypatch):
    monkeypatch.setattr(
        filters.core,
        "get_commands",
        lambda: {"echo one": {"tag": "ops", "description": "Alpha"}},
    )

    result = filters.filter_by_grep(grep="alpha")

    assert result == {"echo one": {"tag": "ops", "description": "Alpha"}}


def test_filter_by_grep_returns_empty_for_no_matches():
    commands = {
        "echo one": {"tag": "ops", "description": "first"},
        "echo two": {"tag": "ops", "description": "second"},
    }

    result = filters.filter_by_grep(commands=commands, grep="nomatch")

    assert result == {}
