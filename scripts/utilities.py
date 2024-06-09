import os 
import json
import shutil
import tempfile

from scripts.config import config, required_local_paths

from collections import defaultdict
from git import Repo

def merge_json_files(folder_path):
    merged_docs = defaultdict(list)
    
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):  # Ensure it's a file
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    doc = json.load(file)
                    if isinstance(doc, dict):  # Ensure the document is a dictionary
                        for key, value in doc.items():
                            if isinstance(value, list):
                                merged_docs[key].extend(value)
                            else:
                                merged_docs[key].append(value)
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from file {file_path}: {e}")
    
    # Convert defaultdict back to a regular dict
    merged_docs = {key: value if len(value) > 1 else value[0] for key, value in merged_docs.items()}
    
    # Write the merged data to 'merged_data.json' in the same folder
    output_file_path = os.path.join(folder_path, "merged_data.json")
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        json.dump(merged_docs, output_file, indent=4)

def prep_local_setup():
    validate_and_create_paths(required_local_paths)
    # Get latest 5e.tools data
    get_5e_tool_data()

def validate_and_create_paths(target_paths):
    for path in target_paths:
        if not os.path.exists(path):
            os.makedirs(path)

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
    
    # Delete and "merged_data.json files from the static/"
    for dirpath, dirnames, filenames in os.walk("static"):
        for filename in filenames:
            if filename == "merged_data.json":
                file_path = os.path.join(dirpath, filename)
                os.remove(file_path)
