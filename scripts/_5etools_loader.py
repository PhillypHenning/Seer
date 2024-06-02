import os
import shutil
import tempfile


from scripts.config import config
from git import Repo

def get_5e_tool_data():
    if config.get("5etools", True):
        if config.get("5etools").get("load_on_startup", True) or not os.path.exists("static/"):
            # Create a tmp directory
            with tempfile.TemporaryDirectory() as tmpdirname:
                if os.path.exists("static"): shutil.rmtree("static")
                # Pull the latest version of 5e.tools repo
                Repo.clone_from("git@github.com:5etools-mirror-2/5etools-mirror-2.github.io.git", tmpdirname)
                # Move the /data to /static
                shutil.move(f"{tmpdirname}/data", "static")
                shutil.rmtree(tmpdirname)
        else: 
            print("Skipping 5eTools data pull")