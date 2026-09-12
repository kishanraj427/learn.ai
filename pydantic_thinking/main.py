from openai import OpenAI
from pydantic import BaseModel
from typing import Literal


# -----------------------------
# Pydantic Response Model
# -----------------------------

class StepResponse(BaseModel):
    step: Literal["START", "PLAN", "OUTPUT"]
    content: str


# -----------------------------
# Ollama Client
# -----------------------------

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

model = "qwen3.5:4b"


# -----------------------------
# System Prompt
# -----------------------------

SYSTEM_PROMPT = """
You are an expert AI Assistant that resolves user queries using a structured
START, PLAN, and OUTPUT process.

Each API call MUST perform EXACTLY ONE step.

Allowed steps:

1. START
   - Understand the user's query.
   - Identify what the user is asking for.

2. PLAN
   - Perform ONE planning action.
   - Return only a concise summary of the current planning action.
   - Do not expose private chain-of-thought.

3. OUTPUT
   - Provide the final answer to the user's query.
   - Return OUTPUT only when planning is sufficient.

Rules:
- First response MUST be START.
- After START, return one or more PLAN responses.
- Finally return OUTPUT.
- Perform exactly ONE step per API call.
"""


messages_history = [
    {
        "role": "system",
        "content": SYSTEM_PROMPT
    }
]

user_query = input("\nWrite your query here.\n👉 ")

messages_history.append({
    "role": "user",
    "content": user_query
})


# -----------------------------
# Agent Loop
# -----------------------------

while True:

    response = client.beta.chat.completions.parse(
        model=model,
        messages=messages_history,
        response_format=StepResponse,
        max_tokens=1024,
        reasoning_effort="none",
        extra_body={
            "think": False
        }
    )

    result = response.choices[0].message.parsed

    if result is None:
        print("⚠️ Failed to parse response")
        continue


    # START
    if result.step == "START":

        print("\n🔥", result.content)

        messages_history.append({
            "role": "assistant",
            "content": result.model_dump_json()
        })

        messages_history.append({
            "role": "user",
            "content": "Now perform exactly one PLAN step."
        })


    # PLAN
    elif result.step == "PLAN":

        print("\n🧠", result.content)

        messages_history.append({
            "role": "assistant",
            "content": result.model_dump_json()
        })

        messages_history.append({
            "role": "user",
            "content": (
                "Now perform exactly one more PLAN step, "
                "or return OUTPUT if planning is sufficient."
            )
        })


    # OUTPUT
    elif result.step == "OUTPUT":

        print("\n🏁", result.content)

        break


# What is the full form of PM of India? and Who is the PM?  