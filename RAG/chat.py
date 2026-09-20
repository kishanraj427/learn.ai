from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI

embedding_model = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"  # default Ollama endpoint
)

vector_store = QdrantVectorStore.from_existing_collection(
    collection_name="resume_collection",
    url="http://localhost:6333",
    embedding=embedding_model
)

# user query for searching the vector store
user_query = input("Enter your query: ")

# Relevant document chunks are retrieved based on the similarity of the query to the stored embeddings
search_results = vector_store.similarity_search_with_score(user_query, k=3)

context = "\n\n\n".join([f"Page {result[0].metadata['page'] + 1}:\n{result[0].page_content}" for result in search_results])

SYSTEM_PROMPT = f"""You are a helpful assistant that answers questions based on the context provided along with PDF Page contents and Page numbers.
If the context does not contain the answer, respond like "I don't know."
Only use numbers, names, and facts that appear verbatim in the context below. Never invent or infer a value that is not explicitly present in the context.
When providing answers, include the page number from which the information was retrieved. If multiple pages are relevant, provide a summary of the information from those pages and include their respective page numbers.

Context:
{context}
"""

model = "qwen3.5:4b"

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

response = client.chat.completions.create(
    model=model,
    messages= [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ],
    reasoning_effort="none",
    extra_body={
        "think": False
    }
)

answer = response.choices[0].message.content

print("CONTENT:", repr(answer))



