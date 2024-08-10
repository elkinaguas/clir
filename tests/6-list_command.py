from clir.cli import ls
from clir.utils.db import get_command_id_from_command, get_tag_id_from_tag, DbIntegrity
from click.testing import CliRunner
import pyperclip, os


def test_list_command():
    cids, _, tids, _, crel, trel = db_integrity_check()
    runner = CliRunner()
    lsresult = runner.invoke(ls)
    cids2, _, tids2, _, crel2, trel2 = db_integrity_check()
    assert lsresult.exit_code == 0
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