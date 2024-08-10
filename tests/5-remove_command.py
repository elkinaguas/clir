from clir.cli import rm, cp
from clir.utils.db import get_command_id_from_command, get_tag_id_from_tag, DbIntegrity
from click.testing import CliRunner
import pyperclip, os


def test_remove_command():
    cids, _, tids, _, crel, trel = db_integrity_check()
    runner = CliRunner()
    result = runner.invoke(rm, input='1\n')
    
    assert result.exit_code == 0

    cpresult = runner.invoke(cp, ['-t', "ansible"], input='1\n')
    assert cpresult.exit_code == 1

    cids2, _, tids2, _, crel2, trel2 = db_integrity_check()
    assert len(cids) - 1 == len(cids2)
    assert len(crel) - 1 == len(crel2)


def test_remove_command_by_tag():
    cids, _, tids, _, crel, trel = db_integrity_check()
    runner = CliRunner()
    result = runner.invoke(rm, ['-t', "c2"], input='1\n')
    cids2, _, tids2, _, crel2, trel2 = db_integrity_check()
    assert result.exit_code == 0

    cpresult = runner.invoke(cp, ['-t', "c2"], input='1\n')
    assert cpresult.exit_code == 1
    assert len(cids) - 1 == len(cids2)
    assert len(crel) - 1 == len(crel2)


def test_remove_command_by_grep():
    cids, _, tids, _, crel, trel = db_integrity_check()
    runner = CliRunner()
    result = runner.invoke(rm, ['-g', "command 3"], input='1\n')
    cids2, _, tids2, _, crel2, trel2 = db_integrity_check()
    assert result.exit_code == 0

    cpresult = runner.invoke(cp, ['-t', "c3"], input='1\n')
    assert cpresult.exit_code == 1
    assert len(cids) - 1 == len(cids2)
    assert len(crel) - 1 == len(crel2)

def test_remove_command_by_tag_and_grep():
    cids, _, tids, _, crel, trel = db_integrity_check()
    runner = CliRunner()
    result = runner.invoke(rm, ['-t', "touch-test", '-g', "file"], input='1\n')
    cids2, _, tids2, _, crel2, trel2 = db_integrity_check()
    assert result.exit_code == 0

    cpresult = runner.invoke(cp, ['-t', "touch-test"], input='1\n')
    assert cpresult.exit_code == 1
    assert len(cids) - 1 == len(cids2)
    assert len(crel) - 1 == len(crel2)


def test_remove_command_not_found():
    cids, _, tids, _, crel, trel = db_integrity_check()
    runner = CliRunner()
    result = runner.invoke(rm, input='100\n')
    cids2, _, tids2, _, crel2, trel2 = db_integrity_check()
    assert result.exit_code == 1
    assert "ID not valid" in result.output
    assert len(cids) == len(cids2)

def db_integrity_check():
    db_integrity = DbIntegrity()
    #commands_ids, commands, tags_ids, tags, cid_relation (commands ids in commands_tags table), tid_relation (commands ids in commands_tags table)
    return db_integrity.main()