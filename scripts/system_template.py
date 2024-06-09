from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def load_default_system_persona():
    chat_template = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful AI bot. You provide accurate data and never lie, fib or make things up."),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    return chat_template
