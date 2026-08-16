from openai import OpenAI
from parse_json import parse_json_response

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

model = "qwen3.5:4b"

# Few Shot Prompting
SYSTEM_PROMPT = """
You are an expert AI Assistant that resolves user queries using a structured
START, PLAN, and OUTPUT process.

IMPORTANT:
Each time you receive a request, you MUST perform EXACTLY ONE step.

The allowed steps are:

1. START
   - Understand the user's query.
   - Identify what the user is asking for.

2. PLAN
   - Perform ONE planning action.
   - The PLAN step may happen across multiple API calls.
   - Each API call must return only ONE PLAN step.
   - Do not expose private chain-of-thought or detailed internal reasoning.
   - Provide only a concise summary of the current planning action.

3. OUTPUT
   - Provide the final answer to the user's query.
   - OUTPUT must only be returned when the task is sufficiently planned.

STRICT RULES:
- Return EXACTLY ONE JSON object per response.
- NEVER return multiple JSON objects.
- NEVER return a JSON array.
- NEVER return JSON followed by additional text.
- NEVER return Markdown outside the JSON object.
- NEVER return more than one step in a single response.
- The "content" field must always be a string.
- Every API call represents exactly ONE step.
- The first response MUST be START.
- After START, return one or more PLAN responses.
- Finally return exactly one OUTPUT response.

JSON FORMAT:

{"step":"START","content":"string"}

OR

{"step":"PLAN","content":"string"}

OR

{"step":"OUTPUT","content":"string"}

EXAMPLE:

User:
What is the capital of France?

First response:
{"step":"START","content":"The user wants to know the capital of France."}

Next response:
{"step":"PLAN","content":"Recall the capital city of France."}

Final response:
{"step":"OUTPUT","content":"The capital of France is Paris."}

"""

messages_history = [
    {"role": "system", "content": SYSTEM_PROMPT },
]
user_query = input("\nWriter your query here.\n👉🏻")
messages_history.append({
    "role": "user",
    "content": user_query}
)

while True:
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=messages_history,
        reasoning_effort="none",
        extra_body={
            "think": False
        }
    )

    answer = response.choices[0].message.content

    # print("CONTENT:", repr(answer))

    if not answer or not answer.strip():
        print("⚠️ Empty response, retrying...")
        continue

    try:
        parsed_answer = parse_json_response(answer)
    except ValueError as e:
        print("⚠️ Invalid JSON:", e)
        continue

    step = parsed_answer.get("step")
    content = parsed_answer.get("content")

    if step == "START":
        print("\n🔥", content)

        messages_history.append({
            "role": "assistant",
            "content": answer
        })

        messages_history.append({
            "role": "user",
            "content": "Now perform exactly one PLAN step."
        })

    elif step == "PLAN":
        print("\n🧠", content)

        messages_history.append({
            "role": "assistant",
            "content": answer
        })

        messages_history.append({
            "role": "user",
            "content": "Now perform exactly one more PLAN step, or return OUTPUT if planning is sufficient."
        })

    elif step == "OUTPUT":
        print("\n🏁", content)
        break

    else:
        print("⚠️ Unknown step:", step)


# What is 2 + 3 * 5?

# What is vande bharat train and when it started operating in india?