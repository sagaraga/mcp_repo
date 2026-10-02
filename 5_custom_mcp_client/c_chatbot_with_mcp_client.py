from langgraph.graph import StateGraph, START
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()  # Load environment variables from .env file

horizon_api_key = os.getenv("HORIZON_API_KEY")
if not horizon_api_key:
    raise RuntimeError("Set HORIZON_API_KEY in 5_custom_mcp_client/.env")

llm = ChatOpenAI(model="gpt-5")

# MCP client for local FastMCP server
client = MultiServerMCPClient(
    {
        "arith": {
            "transport": "stdio",
            "command": "uv",
            "args": [
                "run",
                "--project",
                "/Users/sivasagar/WorkSpace/Python/LangChainGenAI/mcp_repo/3_math-local-mcp-server",
                "python",
                "/Users/sivasagar/WorkSpace/Python/LangChainGenAI/mcp_repo/3_math-local-mcp-server/main.py",
            ],
        },
        "expense": {
            "transport": "streamable_http",  # if this fails, try "sse"
            "url": "https://experienced-pink-anglerfish.fastmcp.app/mcp",
            "headers": {"Authorization": f"Bearer {horizon_api_key}"},
        }
    }
)


# state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


async def build_graph():

    tools = await client.get_tools()

    print(tools)

    llm_with_tools = llm.bind_tools(tools)

    # nodes
    async def chat_node(state: ChatState):

        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {'messages': [response]}

    tool_node = ToolNode(tools)

    # defining graph and nodes
    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    # defining graph connections
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")

    chatbot = graph.compile()

    return chatbot

async def main():

    chatbot = await build_graph()

    # running the graph
    result = await chatbot.ainvoke({"messages": [HumanMessage(content="Add transport expense of 5000 and food expense of 10000 using the expense tracker tool on 30 Sep 2026")]})

    print(result['messages'][-1].content)

if __name__ == '__main__':
    asyncio.run(main())