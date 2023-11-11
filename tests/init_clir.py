import os
import subprocess

subprocess.run(['clir', 'init'], capture_output=True, text=True)
dir_path = os.path.expanduser('~/.clir')
file_path = os.path.expanduser('~/.clir/commands.json')
command_file_creation_time = os.path.getctime(file_path)

# Test if the clir folder environment was created
def test_clir_project_folder_created():
    assert os.path.exists(dir_path)

# Test if the commands.json file was created
def test_command_file_created():
    assert os.path.exists(file_path)

# Test if init command doesn't recreate the commands.json file
def test_init_command_doesnt_recreate_commands_json():
    subprocess.run(['clir', 'init'], capture_output=True, text=True)
    assert os.path.getctime(file_path) == command_file_creation_time