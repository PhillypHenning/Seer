from scripts.config import config
from scripts.toolbelt_loader import create_adventurer_toolbelt
from scripts.system_template import load_default_system_persona
from scripts.utilities import validate_and_create_paths, prep_local_setup

from fastapi import FastAPI
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langserve import add_routes
from typing import List


# Prep local
prep_local_setup()

toolbelt = create_adventurer_toolbelt()

# Get prepped system template
# system_template = load_default_system_persona()
system_template = hub.pull("hwchase17/openai-functions-agent")

# Instantiate LLM and AI agent
llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=config.get("openai").get("api_key"))
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
