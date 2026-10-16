from langchain_core.messages import HumanMessage

from app.agent import agent


if __name__ == "__main__":
    result = agent.invoke({
        "messages": [
            HumanMessage(
                content="Why did customer C003's bill increase from July 2026 to August 2026?"
            )
        ]
    })

    for message in result["messages"]:
        print("\nMESSAGE TYPE:", type(message).__name__)

        if getattr(message, "tool_calls", None):
            print("TOOL CALLS:", message.tool_calls)

        print("CONTENT:", message.content)
        print("-" * 50)
