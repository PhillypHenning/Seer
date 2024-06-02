from scripts.config import config
from scripts.data_loaders import load_multifile_unstruct_markdown, load_multifile_jsondata, load_data_jsonfile
from langchain.tools.retriever import create_retriever_tool
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Instantiate embedding model and vector store
embeddings = OpenAIEmbeddings(api_key=config.get("openai").get("api_key"))

def create_adventurer_toolbelt():
    toolbelt = []

    if config.get("toolbelt", True):
        if config.get("toolbelt").get("rules", {"enable": True} ).get("enable"):
            # Create tool for 5e rules lookup
            toolbelt = toolbelt + prep_5e_rules_data()
    
    if config.get("toolbelt", True):
        if config.get("toolbelt").get("adventure", {"enable": True} ).get("enable"):
            # Create tool for adventure details lookup
            toolbelt += prep_adventure_data()

    if config.get("toolbelt", False):
        if config.get("toolbelt").get("notes", {"enable": False} ).get("enable"):
            # Create tool for DM Notes
            dm_data = prep_dm_data()
            if dm_data:
                    toolbelt += dm_data

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
    docs = load_data_jsonfile("static/adventure/adventure-wbtw.json", ".data")
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
    print("Loading 5e rules data")
    
    # Load bestiaries
    docs = load_multifile_jsondata("static/bestiary", ".monster")
    vector = FAISS.from_documents(docs, embeddings)
    retriever = vector.as_retriever()
    tool = create_retriever_tool(
        retriever=retriever,
        name="search_in_rules_for_monster",
        description="When you need to search for information about a Monster use this tool. If you want to gather more information about specific monsters that you are unsure of use this tool."
    )
    toolbelt += tool

    # Load rulebooks
    docs = load_multifile_jsondata("static/book", ".data")
    vector = FAISS.from_documents(docs, embeddings)
    retriever = vector.as_retriever()
    tool = create_retriever_tool(
        retriever=retriever,
        name="search_in_rules_for_rule",
        description="When you need to search for information about a Dungeons and Dragons rule use this tool. If you want to gather more information about a specific rule that you are unsure of use this tool."
    )
    toolbelt += tool

    # Load classes
    docs += load_multifile_jsondata("static/class", ".class")

    # Load spells
    docs += load_multifile_jsondata("static/spells", ".spell")

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
    retriever = vector.as_retriever()
    rules_search_tool = create_retriever_tool(
        retriever=retriever,
        name="search_in_rules",
        description="When you need to search for information about Dungeons and Dragons rules use this tool. If you want to gather more information about speficic nouns or topics that you are unsure of from the Adventure check this tool."
    )
    return toolbelt
