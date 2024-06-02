import tempfile
import shutil
import os
import json

from scripts.config import config
from git import Repo
from collections import defaultdict
from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS


# Instantiate embedding model and vector store
embeddings = OpenAIEmbeddings(api_key=config.get("openai").get("api_key"))
text_splitter = RecursiveCharacterTextSplitter()

def get_5e_tool_data():
    if config.get("5etools", None):
        if config.get("5etools").get("load_on_startup", None) or not os.path.exists("static/"):
            # Create a tmp directory
            with tempfile.TemporaryDirectory() as tmpdirname:
                if os.path.exists("static"): shutil.rmtree("static")
                # Pull the latest version of 5e.tools repo
                Repo.clone_from("git@github.com:5etools-mirror-2/5etools-mirror-2.github.io.git", tmpdirname)
                # Move the /data to /static
                shutil.move(f"{tmpdirname}/data", "static")
                shutil.rmtree(tmpdirname)
        else: 
            print("Config.5etools.load_on_startup set to False")
    else:
        print("Config.5etools not set")

def prep_adventure_data():
    print("Loading Adventure data")
    docs = load_data_file("static/adventure/adventure-wbtw.json", ".data")
    vector = FAISS.from_documents(docs, embeddings)
    retriever = vector.as_retriever()
    adventure_search_tool = create_retriever_tool(
        retriever=retriever,
        name="search_in_adventure_doc",
        description="When you need to search for information about the \"Wilds Beyond the Witchlight\" Dungeons and Dragons adventure use this tool. Also refer to this tool when someone uses the acronym WBTW, WBtW or wbtw"
    )
    return adventure_search_tool

def prep_5e_rules_data():
    # https://python.langchain.com/v0.1/docs/modules/data_connection/retrievers/parent_document_retriever/
    toolbelt = []
    # docs = []
    print("Loading rules")
    # Load bestiaries
    docs = load_multifile_data("static/bestiary", ".monster")
    vector = FAISS.from_documents(docs, embeddings)
    retriever = vector.as_retriever()
    tool = create_retriever_tool(
        retriever=retriever,
        name="search_in_rules_for_monster",
        description="When you need to search for information about a Monster use this tool. If you want to gather more information about specific monsters that you are unsure of use this tool."
    )
    toolbelt += tool

    # Load rulebooks
    docs = load_multifile_data("static/book", ".data")
    vector = FAISS.from_documents(docs, embeddings)
    retriever = vector.as_retriever()
    tool = create_retriever_tool(
        retriever=retriever,
        name="search_in_rules_for_rule",
        description="When you need to search for information about a Dungeons and Dragons rule use this tool. If you want to gather more information about a specific rule that you are unsure of use this tool."
    )
    toolbelt += tool

    # # Load classes
    # docs += load_multifile_data("static/class", ".class")

    # # Load spells
    # docs += load_multifile_data("static/spells", ".spell")

    # # Load actions
    # docs += load_data_file("static/actions.json", ".action")

    # # Load books
    # docs += load_data_file("static/books.json", ".book")

    # # Load backgrounds
    # docs += load_data_file("static/backgrounds.json", ".background")

    # # Load conditions
    # docs += load_data_file("static/conditionsdiseases.json", ".condition")
    # # Load diseases
    # docs += load_data_file("static/conditionsdiseases.json", ".disease")

    # # Load deities
    # docs += load_data_file("static/deities.json", ".deity")

    # # Load feats
    # docs += load_data_file("static/feats.json", ".feat")

    # # Load items
    # docs += load_data_file("static/items.json", ".item")
    
    # # Load languages
    # docs += load_data_file("static/languages.json", ".language")

    # # Load magicvariants
    # docs += load_data_file("static/magicvariants.json", ".magicvariant")

    # # Load names
    # docs += load_data_file("static/names.json", ".name")

    # # Load objects
    # docs += load_data_file("static/objects.json", ".object")
    
    # # Load races
    # docs += load_data_file("static/races.json", ".race")
    
    # # Load recipes
    # docs += load_data_file("static/recipes.json", ".recipe")
    
    # # Load senses
    # docs += load_data_file("static/senses.json", ".sense")
    
    # # Load skills
    # docs += load_data_file("static/skills.json", ".skill")

    # # Load traps
    # docs += load_data_file("static/trapshazards.json", ".trap")
    # # Load hazards
    # docs += load_data_file("static/trapshazards.json", ".hazard")

    # # Load vehicles
    # docs += load_data_file("static/vehicles.json", ".vehicle")
    
    # vector = FAISS.from_documents(docs, embeddings)
    # retriever = vector.as_retriever()
    # rules_search_tool = create_retriever_tool(
    #     retriever=retriever,
    #     name="search_in_rules",
    #     description="When you need to search for information about Dungeons and Dragons rules use this tool. If you want to gather more information about speficic nouns or topics that you are unsure of from the Adventure check this tool."
    # )
    return toolbelt

def load_multifile_data(folder_path, jq_schema):
    docs = merge_json_files(folder_path)    
    loader = JSONLoader(
        file_path=f"{folder_path}/merged_data.json",
        jq_schema=jq_schema,
        text_content=False
    )
    doc = loader.load()
    return text_splitter.split_documents(doc)


def load_data_file(file_path, jq_schema):
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=jq_schema,
        text_content=False
    )
    doc = loader.load()
    return text_splitter.split_documents(doc)


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