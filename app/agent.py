from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState,StateGraph, START
from langgraph.prebuilt import ToolNode,tools_condition
from app.prompts import BILLING_AGENT_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage

from app.tools.customer import get_customer
from app.tools.billing import get_billing_info
from app.tools.usage import get_usage_info
from app.tools.rate_plan import get_rate_plan


load_dotenv()


model = ChatOpenAI(
    model="gpt-6-luna"
)


tools = [
    get_customer,
    get_billing_info,
    get_usage_info,
    get_rate_plan,
]

tool_node = ToolNode(tools)
model_with_tools = model.bind_tools(tools)

def call_model(state: MessagesState):
    messages = [SystemMessage(content=BILLING_AGENT_SYSTEM_PROMPT)] + state["messages"]
    response = model_with_tools.invoke(
        messages
    )

    return {
        "messages": [response]
    }
builder = StateGraph(MessagesState)

builder.add_node("agent", call_model)
builder.add_node("tools", tool_node)
builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    tools_condition
)
builder.add_edge("tools", "agent")
agent = builder.compile()