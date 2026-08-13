from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

# Zero Shot promting
SYSTEM_PROMT = "You are an expert in coding and data structure and aglo problem solver. And only and only answer question related to coding."

# Few Shot promting
SYSTEM_PROMT = """You are an expert in coding and data structure and aglo problem solver. 
And only and only answer question related to coding.

Examples: Can u explain who to write code of to calculate root of number
Answer: ...
"""


response = client.chat.completions.create(
    model="qwen3.5:4b",
    messages=[
        {
            "role": "system",
            "content": SYSTEM_PROMT 
        },
        {
            "role": "user",
            "content": "How to write program to generate table of any number by taking input. Use lang as Python"
        }
    ],
)

print(response.choices[0].message.content)