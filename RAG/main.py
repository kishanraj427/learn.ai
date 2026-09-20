from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore

pdf_path = Path(__file__).parent / "data" / "resume.pdf"

# Initialize the loader with a local or online PDF path
loader = PyPDFLoader(file_path=pdf_path)

# Load all pages into a list of Document objects
pages = loader.load()

# Print the content of the first page
print(pages[0].page_content)
print(pages[0].metadata)


# Split the content of the first page into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(pages)

# Create vector embeddings for each chunk using OpenAI's embedding model
# embeddings = OpenAIEmbeddings(
#     model="text-embedding-3-large"
# )
embedding_model = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"  # default Ollama endpoint
)

vector_store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    collection_name="resume_collection",
    url="http://localhost:6333"
)

print(f"Number of chunks created: {len(chunks)}")
