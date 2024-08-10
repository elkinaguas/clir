from clir.cli import run
from clir.utils.db import get_command_id_from_command, get_tag_id_from_tag, DbIntegrity
from click.testing import CliRunner
import pyperclip, os

# Check:
# - That the output corresponds to the one of the command
def test_run_command():
    cids, _, tids, _, crel, trel = db_integrity_check()
    runner = CliRunner()
    runresult = runner.invoke(run, ['-t', "touch-test"], input='1\n')
    cids2, _, tids2, _, crel2, trel2 = db_integrity_check()
    assert runresult.exit_code == 0
    assert os.path.exists(os.path.expanduser('~/.clir/test-file.txt')) == True
    assert len(cids) == len(cids2)
    assert len(tids) == len(tids2)
    assert len(crel) == len(crel2)
    assert set(cids) == set(cids2)
    assert set(tids) == set(tids2)
    assert set(crel) == set(crel2)
    assert set(trel) == set(trel2)


# Check:
# - That the output corresponds to the one of the command not found message
def test_run_command_not_found():
    cids, _, tids, _, crel, trel = db_integrity_check()
    runner = CliRunner()
    runresult = runner.invoke(run, ['-t', "touch-test"], input='100\n')
    cids2, _, tids2, _, crel2, trel2 = db_integrity_check()
    assert runresult.exit_code == 1
    assert "ID not valid" in runresult.output
    assert len(cids) == len(cids2)
    assert len(tids) == len(tids2)
    assert len(crel) == len(crel2)
    assert set(cids) == set(cids2)
    assert set(tids) == set(tids2)
    assert set(crel) == set(crel2)
    assert set(trel) == set(trel2)


def db_integrity_check():
    db_integrity = DbIntegrity()
    #commands_ids, commands, tags_ids, tags, cid_relation (commands ids in commands_tags table), tid_relation (commands ids in commands_tags table)
    return db_integrity.main()