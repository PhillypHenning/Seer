import os 
import json

from collections import defaultdict

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