import tempfile
import shutil
import os

from git import Repo
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_5e_tool_data():
    # Create a tmp directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        shutil.rmtree("static")
        # Pull the latest version of 5e.tools repo
        Repo.clone_from("git@github.com:5etools-mirror-2/5etools-mirror-2.github.io.git", tmpdirname)
        # Move the /data to /static
        shutil.move(f"{tmpdirname}/data", "static")
        shutil.rmtree(tmpdirname)

def prep_adventure_data():
    return load_data_file("static/adventure/adventure-wbtw.json", ".data")

def prep_5e_rules_data():
    load_multifile_data("static/bestiary", ".monster")
    # Load bestiaries
    # Load rulebooks
    # Load classes
    # Load spells
    # Load actions
    # Load deities
    # Load items
    # Load languages
    # Load races
    # Load recipes
    # Load senses
    # Load skills
    pass

def load_multifile_data(folder_path, jq_schema):
    text_splitter = RecursiveCharacterTextSplitter()

    docs = []
    for file in os.listdir(folder_path):
        file_path=f"{folder_path}/{file}"
        loader = JSONLoader(
            file_path=file_path,
            jq_schema=jq_schema,
            text_content=False
        )
        doc = loader.load()
        docs.append(text_splitter.split_documents(doc))

    return docs


def load_data_file(file_path, jq_schema):
    text_splitter = RecursiveCharacterTextSplitter()
    
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=jq_schema,
        text_content=False
    )
    doc = loader.load()
    docs = text_splitter.split_documents(doc)

    return docs
