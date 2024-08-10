from clir.cli import new, cp
from clir.utils.db import get_command_id_from_command, get_tag_id_from_tag, DbIntegrity
from click.testing import CliRunner
import pyperclip, os


# Test add new command using flags
def test_add_new_command():
    cids, _, tids, _, crel, _ = db_integrity_check()
    runner = CliRunner()
    result = runner.invoke(new, ['-c', "command 1", '-d', "Command 1 description", '-t', "c1"])
    echo_test_result = runner.invoke(new, ['-c', "touch ~/.clir/test-file.txt", '-d', "Create a test file", '-t', "touch-test"])
    cids2, _, tids2, _, crel2, _ = db_integrity_check()
    assert result.exit_code == 0
    assert echo_test_result.exit_code == 0

    cpresult = runner.invoke(cp, ['-t', "c1"], input='1\n')
    assert cpresult.exit_code == 0
    assert pyperclip.paste() == "command 1"
    
    cpechotestresult = runner.invoke(cp, ['-t', "touch-test"], input='1\n')
    assert cpechotestresult.exit_code == 0
    assert pyperclip.paste() == "touch ~/.clir/test-file.txt"
    assert os.path.exists(os.path.expanduser('~/.clir/test-file.txt')) == False
    assert len(cids) + 2 == len(cids2)
    assert len(tids) + 2 == len(tids2)
    assert len(crel) + 2 == len(crel2)

def test_add_new_command_with_prompt():
    cids, _, tids, _, crel, _ = db_integrity_check()
    runner = CliRunner()
    result = runner.invoke(new, input='\n'.join(["command 2", "Command 2 description", "c2"]))
    cpresult = runner.invoke(cp, ['-t', "c2"], input='1\n')
    cids2, _, tids2, _, crel2, _ = db_integrity_check()
    assert result.exit_code == 0
    assert cpresult.exit_code == 0
    assert pyperclip.paste() == "command 2"
    assert len(cids) + 1 == len(cids2)
    assert len(tids) + 1 == len(tids2)
    assert len(crel) + 1 == len(crel2)

def test_add_fourth_command_with_prompt():
    cids, _, tids, _, crel, _ = db_integrity_check()
    runner = CliRunner()
    result = runner.invoke(new, input='\n'.join(["command 3", "Command 3 great description", "c3"]))
    cpresult = runner.invoke(cp, ['-t', "c3"], input='1\n')
    cids2, _, tids2, _, crel2, _ = db_integrity_check()
    assert result.exit_code == 0
    assert cpresult.exit_code == 0
    assert pyperclip.paste() == "command 3"
    assert len(cids) + 1 == len(cids2)
    assert len(tids) + 1 == len(tids2)
    assert len(crel) + 1 == len(crel2)
    

# Check 3 things:
# - That the command that already exists still has his original id
# - That the tag of the command that already exists has the same id
# - That there is no a new entry in the commandd_tags table
def test_add_existing_command():
    cids, _, tids, _, crel, trel = db_integrity_check()
    runner = CliRunner()
    old_command_id = get_command_id_from_command("command 1")
    old_tag_id = get_tag_id_from_tag("c1")
    result = runner.invoke(new, ['-c', "command 1", '-d', "Command 1 description", '-t', "c1"])
    new_command_id = get_command_id_from_command("command 1")
    new_tag_id = get_tag_id_from_tag("c1")
    cids2, _, tids2, _, crel2, trel2 = db_integrity_check()
    assert result.exit_code == 0
    assert old_command_id == new_command_id
    assert old_tag_id == new_tag_id
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
