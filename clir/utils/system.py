import subprocess

def verify_xclip_installation(package: str = ""):
    if package == "xclip":
        try:
            subprocess.run(["xclip", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    if package == "pbcopy":
        try:
            subprocess.run(["pbcopy", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    
    return "No package specified"