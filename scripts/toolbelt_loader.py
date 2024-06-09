import os 

from scripts.config import config
from scripts.data_loaders import load_multifile_unstruct_markdown, load_multifile_jsondata, load_data_jsonfile
from langchain.tools.retriever import create_retriever_tool
from langchain_openai import OpenAIEmbeddings
# from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# Instantiate embedding model and vector store
embeddings = OpenAIEmbeddings(api_key=config.get("openai").get("api_key"))

def create_adventurer_toolbelt():
    toolbelt = []

    if config.get("toolbelt", True):
        if config.get("toolbelt").get("rules", {"enable": True} ).get("enable"):
            # Create tool for 5e rules lookup
            toolbelt += [prep_5e_rules_data()]
            toolbelt += [prep_5e_beastiary_data()]
            toolbelt += [prep_5e_spells_data()]

    if config.get("toolbelt", True):
        if config.get("toolbelt").get("adventure", {"enable": True} ).get("enable"):
            # Create tool for adventure details lookup
            toolbelt += [prep_adventure_data()]

    if config.get("toolbelt", False):
        if config.get("toolbelt").get("notes", {"enable": False} ).get("enable"):
            # Create tool for DM Notes
            dm_data = prep_dm_data()
            if dm_data:
                toolbelt += [dm_data]

    return toolbelt





def prep_dm_data():
    if (not config.get("toolbelt").get("notes").get("location")
     or not config.get("toolbelt").get("notes").get("type")
     or not config.get("toolbelt").get("notes").get("format_description")):
        print("""Missing required configuration:
    config.toolbelt.notes.location is required
    config.toolbelt.notes.type is required
    config.toolbelt.notes.format_description is required
Unable to load DM Data.""")
        return None
    
    location = config.get("toolbelt").get("notes").get("location")
    data_type = config.get("toolbelt").get("notes").get("type")
    format_description = config.get("toolbelt").get("notes").get("format_description")    

    supported_data_types = ["UnstructuredMarkdown"]
    if data_type not in supported_data_types:
        print(f"Unsupport data type: {data_type}, please use one of the following: {supported_data_types}")


    if data_type == "UnstructuredMarkdown":
        docs = load_multifile_unstruct_markdown(location)

def prep_adventure_data():
    print("Loading Adventure data")

    # Look for the data locally
    if not os.path.exists("data/vectors/adventure_data.vector"):
        print("No adventure data vector data found.. generating new vectors")
        docs = load_data_jsonfile("static/adventure/adventure-wbtw.json", ".data")
        vector = FAISS.from_documents(docs, embeddings)
        vector.save_local("data/vectors/adventure_data.vector")
    else:
        print("Local adventure data vector data found, loading vectors")
        vector = FAISS.load_local("data/vectors/adventure_data.vector", embeddings, allow_dangerous_deserialization=True)

    retriever = vector.as_retriever()
    adventure_search_tool = create_retriever_tool(
        retriever=retriever,
        name="search_in_adventure_doc",
        description="When you need to search for information about the \"Wilds Beyond the Witchlight\" Dungeons and Dragons adventure use this tool. Also refer to this tool when someone uses the acronym WBTW, WBtW or wbtw"
    )
    return adventure_search_tool

def prep_5e_beastiary_data():
    print("Loading 5e beastiary data")
    # Look for the data locally
    if not os.path.exists("data/vectors/5e_beastiary.vector"):
        print("No beastiary vector data found.. generating new vectors")
        docs = load_multifile_jsondata("static/bestiary", ".monster")

        vector = FAISS.from_documents(docs, embeddings)
        vector.save_local("data/vectors/5e_beastiary.vector")
    else:
        print("Local beastiary vector data found, loading vectors")
        vector = FAISS.load_local("data/vectors/5e_beastiary.vector", embeddings, allow_dangerous_deserialization=True)
    
    retriever = vector.as_retriever()
    beastiary_tool = create_retriever_tool(
        retriever=retriever,
        name="search_in_rules_for_monster",
        description="When you need to search for information about a Monster use this tool. If you want to gather more information about specific monsters that you are unsure of use this tool."
    )
    return beastiary_tool


def prep_5e_spells_data():
    print("Loading 5e spells data")
    # Look for the data locally
    if not os.path.exists("data/vectors/5e_spells.vector"):
        print("No spells vector data found.. generating new vectors")
        docs = load_multifile_jsondata("static/spells", ".spell")

        vector = FAISS.from_documents(docs, embeddings)
        vector.save_local("data/vectors/5e_spells.vector")
    else:
        print("Local spells vector data found, loading vectors")
        vector = FAISS.load_local("data/vectors/5e_spells.vector", embeddings, allow_dangerous_deserialization=True)
    
    retriever = vector.as_retriever()
    spells_tool = create_retriever_tool(
        retriever=retriever,
        name="search_in_rules_for_spells",
        description="When you need to search for information about a Spell use this tool. If you want to gather more information about specific spells that you are unsure of use this tool."
    )
    return spells_tool

def prep_5e_rules_data():
    # https://python.langchain.com/v0.1/docs/modules/data_connection/retrievers/parent_document_retriever/
    print("Loading 5e rules data")

    # Look for the data locally
    if not os.path.exists("data/vectors/5e_rules.vector"):
        print("No rules vector data found.. generating new vectors")
        
        # Load classes
        docs = load_multifile_jsondata("static/class", ".class")

        # Load actions
        docs += load_data_jsonfile("static/actions.json", ".action")

        # Load books
        docs += load_data_jsonfile("static/books.json", ".book")

        # Load backgrounds
        docs += load_data_jsonfile("static/backgrounds.json", ".background")

        # Load conditions
        docs += load_data_jsonfile("static/conditionsdiseases.json", ".condition")
        # Load diseases
        docs += load_data_jsonfile("static/conditionsdiseases.json", ".disease")

        # Load deities
        docs += load_data_jsonfile("static/deities.json", ".deity")

        # Load feats
        docs += load_data_jsonfile("static/feats.json", ".feat")

        # Load items
        docs += load_data_jsonfile("static/items.json", ".item")
        
        # Load languages
        docs += load_data_jsonfile("static/languages.json", ".language")

        # Load magicvariants
        docs += load_data_jsonfile("static/magicvariants.json", ".magicvariant")

        # Load names
        docs += load_data_jsonfile("static/names.json", ".name")

        # Load objects
        docs += load_data_jsonfile("static/objects.json", ".object")
        
        # Load races
        docs += load_data_jsonfile("static/races.json", ".race")
        
        # Load recipes
        docs += load_data_jsonfile("static/recipes.json", ".recipe")
        
        # Load senses
        docs += load_data_jsonfile("static/senses.json", ".sense")
        
        # Load skills
        docs += load_data_jsonfile("static/skills.json", ".skill")

        # Load traps
        docs += load_data_jsonfile("static/trapshazards.json", ".trap")
        # Load hazards
        docs += load_data_jsonfile("static/trapshazards.json", ".hazard")

        # Load vehicles
        docs += load_data_jsonfile("static/vehicles.json", ".vehicle")
        
        vector = FAISS.from_documents(docs, embeddings)
        vector.save_local("data/vectors/5e_rules.vector")
    else:
        print("Local rules vector data found, loading vectors")
        vector = FAISS.load_local("data/vectors/5e_rules.vector", embeddings, allow_dangerous_deserialization=True)

    retriever = vector.as_retriever()
    rules_search_tool = create_retriever_tool(
        retriever=retriever,
        name="search_in_rules",
        description="When you need to search for information about Dungeons and Dragons rules use this tool. If you want to gather more information about speficic nouns or topics that you are unsure of from the Adventure check this tool."
    )
    return rules_search_tool
