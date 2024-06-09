from langchain_community.document_loaders import JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from scripts.utilities import merge_json_files


text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)


def load_multifile_jsondata(folder_path, jq_schema):
    docs = merge_json_files(folder_path)    
    loader = JSONLoader(
        file_path=f"{folder_path}/merged_data.json",
        jq_schema=jq_schema,
        text_content=False
    )
    doc = loader.load()
    return text_splitter.split_documents(doc)


def load_data_jsonfile(file_path, jq_schema):
    loader = JSONLoader(
        file_path=file_path,
        jq_schema=jq_schema,
        text_content=False
    )
    doc = loader.load()
    return text_splitter.split_documents(doc)

def load_multifile_unstruct_markdown(folder_path):
    pass