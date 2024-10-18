import os
import json
from clir.cli import export, imports
from clir.utils.db import DbIntegrity
from click.testing import CliRunner

def test_export_command():
    cids, _, tids, _, crel, trel = db_integrity_check()
    runner = CliRunner()
    result = runner.invoke(export)
    
    assert result.exit_code == 0
    assert os.path.exists("commands.json")
    
    with open("commands.json", "r") as f:
        exported_commands = json.load(f)
    
    assert len(exported_commands) == len(cids)
    
    os.remove("commands.json")
    
    cids2, _, tids2, _, crel2, trel2 = db_integrity_check()
    assert len(cids) == len(cids2)
    assert len(tids) == len(tids2)
    assert len(crel) == len(crel2)
    assert set(cids) == set(cids2)
    assert set(tids) == set(tids2)
    assert set(crel) == set(crel2)
    assert set(trel) == set(trel2)

def test_import_command():
    cids, commands, tids, tags, crel, trel = db_integrity_check()
    
    # Create a temporary file with some commands to import
    import_data = {
        "new_command": {
            "description": "New command description",
            "tag": "new_tag",
            "creation_date": "2023-01-01 00:00:00.000",
            "last_modif_date": "2023-01-01 00:00:00.000"
        },
        "existing_command": {
            "description": "Updated description",
            "tag": "updated_tag",
            "creation_date": "2023-01-01 00:00:00.000",
            "last_modif_date": "2023-01-02 00:00:00.000"
        }
    }
    
    with open("temp_import.json", "w") as f:
        json.dump(import_data, f)
    
    runner = CliRunner()
    result = runner.invoke(imports, ['-f', 'temp_import.json'])
    
    assert result.exit_code == 0
    
    cids2, commands2, tids2, tags2, crel2, trel2 = db_integrity_check()
    
    assert len(cids2) >= len(cids) + 1  # At least one new command added
    assert "new_command" in commands2
    assert "new_tag" in tags2
    
    # Clean up
    os.remove("temp_import.json")

def db_integrity_check():
    db_integrity = DbIntegrity()
    return db_integrity.main()
