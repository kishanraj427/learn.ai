## Format
# Note: INST -> Instructions

# [INST] What is the time now? [/INST]

"""
<s>[INST]
You are an expert AI assistant.

You must process the user's request using:
1. START
2. PLAN
3. OUTPUT

Perform exactly one step at a time.

User request:
What is RAG?
[/INST]
{"step":"START","content":"The user wants to understand RAG."}
</s>
"""

# Important: [INST] is not a universal prompting format. It is a model/chat-template convention. With Ollama, you generally should not manually add [INST] unless the specific model's template expects it; Ollama's chat API can apply the model's template for you.