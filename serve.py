# Project files
from scripts.config import config

# Required Modules
from fastapi import FastAPI
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_community.vectorstores import FAISS
from langchain_core.messages import BaseMessage
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langserve import add_routes
from typing import List

# Prep adventure data
loader = UnstructuredMarkdownLoader("static/The_Wild_Beyond_the_Witchlight.md")
adventure_doc = loader.load()
text_splitter = RecursiveCharacterTextSplitter()
adventure_docs = text_splitter.split_documents(adventure_doc)

# Instantiate embedding model and vector store
embeddings = OpenAIEmbeddings(api_key=config.get("openai").get("api_key"))
vector = FAISS.from_documents(adventure_docs, embeddings)

# Instantiate retriever
retriever = vector.as_retriever()

# Instantiate toolbelt
adventure_search_tool = create_retriever_tool(
    retriever=retriever,
    name="search_in_adventure_doc",
    description="When you need to search for information about the \"Wilds Beyond the Witchlight\" DnD adventure use this tool."
)
toolbelt = [adventure_search_tool]

# Get prepped system template
system_template = hub.pull("hwchase17/openai-functions-agent")


# Instantiate LLM and AI agent
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, api_key=config.get("openai").get("api_key"))
seer = create_openai_functions_agent(llm, toolbelt, system_template)
agent_executor = AgentExecutor(agent=seer, tools=toolbelt, verbose=True)

# Create API
app = FastAPI(
    title="Seer AI",
    version="0.0.1"
)

class Input(BaseModel):
    input: str
    chat_history: List[BaseMessage] = Field(
        ...,
        extra={"widget": {"type": "chat", "input": "location"}},
    )


class Output(BaseModel):
    output: str

add_routes(
    app,
    agent_executor.with_types(input_type=Input, output_type=Output),
    path="/agent",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)