from openai import OpenAI
import requests
import json


client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

MODEL = "qwen3.5:4b"


# Tools
def get_weather(city: str) -> str:
    """Get the current weather for a city."""

    try:
        url = f"https://wttr.in/{city}?format=%C+%t"

        response = requests.get(
            url,
            timeout=10
        )

        response.raise_for_status()

        return f"The weather in {city} is {response.text.strip()}."

    except requests.RequestException as e:
        return f"Unable to get weather for {city}: {e}"


# Tool Registry
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
}


# Tool Schemas
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Name of the city.",
                    }
                },
                "required": ["city"],
            },
        },
    }
]


# System Prompt
SYSTEM_PROMPT = """
You are a helpful AI assistant.

Use tools when they are necessary.

For weather-related questions, always use the get_weather tool.

Do not make up tool results.

If no tool is required, answer the user directly.
"""


# ==============================
# Messages
# ==============================

messages = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }
]


# Tool Executor
def execute_tool(tool_call):

    tool_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)

    tool = AVAILABLE_TOOLS.get(tool_name)

    if not tool:
        return f"Tool '{tool_name}' not found."

    try:
        return tool(**arguments)

    except Exception as e:
        return f"Tool execution failed: {e}"


# Agent
def run_agent(user_query: str):

    messages.append({
        "role": "user",
        "content": user_query,
    })

    while True:

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            reasoning_effort="none",
            extra_body={
                "think": False,
            },
        )

        assistant_message = response.choices[0].message

        # Final answer
        if not assistant_message.tool_calls:
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
            })
            return assistant_message.content

        # Store assistant tool call
        messages.append(assistant_message)

        # Execute tools
        for tool_call in assistant_message.tool_calls:

            result = execute_tool(tool_call)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })


# CLI
while True:

    user_query = input("\nEnter your query\n👉🏻 ")

    if user_query.lower() in {
        "exit",
        "quit",
    }:
        break

    answer = run_agent(user_query)

    print(f"\n🤖 {answer}")