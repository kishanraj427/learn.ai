import tiktoken

conversion = tiktoken.encoding_for_model("gpt-4o")

msg = "Hi, My name is kishan"

tokens = conversion.encode(msg)

print(tokens)
# [12194, 11, 3673, 1308, 382, 97162, 270]

oldMsg = conversion.decode(tokens)

print(oldMsg)
# Hi, My name is kishan
