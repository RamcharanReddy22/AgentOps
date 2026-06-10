import os
from typing import Annotated, TypedDict, Sequence
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from tools.market_tools import all_tools

load_dotenv()

GROQ_API_KEY = os.getenv("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")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The history of conversation messages"]

# Initialize the Groq client and bind tools
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    api_key=GROQ_API_KEY,
    temperature=0.0  # Force maximum determinism to eliminate spacing issues
).bind_tools(all_tools)

# Strict instruction guiding the Groq model on formatting parameters
SYSTEM_PROMPT = SystemMessage(
    content="You are an expert market analyst with access to local documents. "
            "When calling a tool, you must generate your function arguments cleanly "
            "as a single line, compressed JSON object with zero extra whitespaces or newlines."
)

def run_agent_node(state: AgentState):
    # Inject our structural instruction at the beginning of the context loop
    current_messages = [SYSTEM_PROMPT] + list(state["messages"])
    response = llm.invoke(current_messages)
    return {"messages": [response]}

def should_continue_loop(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "execute_tools"
    return END

# Build graph topology mapping
workflow = StateGraph(AgentState)
workflow.add_node("agent", run_agent_node)
workflow.add_node("action", ToolNode(all_tools))

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue_loop, {"execute_tools": "action", END: END})
workflow.add_edge("action", "agent")

compiled_market_graph = workflow.compile()
