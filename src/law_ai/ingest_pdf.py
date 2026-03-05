import os
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PDF_PATH = os.path.join(BASE_DIR, "data", "BNS_2023.pdf")
CHROMA_DB_PATH = os.path.join(BASE_DIR, "data", "chroma_db")
COLLECTION_NAME = "legal_kb"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


print("🚀 Starting Smart Law Ingestion Pipeline...")

# 1. Load the PDF
if not os.path.exists(PDF_PATH):
    raise FileNotFoundError(f"❌ Please place your PDF at: {PDF_PATH}")

print(f"📄 Reading PDF: {PDF_PATH}")
loader = PyPDFLoader(PDF_PATH)
pages = loader.load()

# 2. Smart Legal Text Splitting
# We tell the splitter to prioritize keeping Sections and Chapters together!
print("✂️ Chunking text using legal-aware separators...")
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\nCHAPTER ", "\nSection ", "\n\n", "\n", "."],
    chunk_size=1200,
    chunk_overlap=200,
    length_function=len,
)
chunks = text_splitter.split_documents(pages)
print(f"✅ Generated {len(chunks)} smart text chunks.")

# 3. Initialize Embedding Model
print("🧠 Loading Embedding Model (all-MiniLM-L6-v2)...")
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device='cuda')

# 4. Connect to ChromaDB
print("🗄️ Connecting to Vector Database...")
client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)

# 5. Ingest into Database
print("⏳ Embedding and saving to ChromaDB. This might take a minute...")
documents = []
metadatas = []
ids = []
embeddings = []

for i, chunk in enumerate(chunks):
    text = chunk.page_content
    # Clean up random PDF newlines
    text = text.replace("-\n", "").replace("\n", " ").strip()

    # Extract page number for citations
    page_num = chunk.metadata.get("page", "Unknown")

    documents.append(text)
    metadatas.append({"source": f"BNS_2023.pdf - Page {page_num}", "type": "Statute"})
    ids.append(f"bns_chunk_{i}")

    # Generate the vector embedding
    vector = embedding_model.encode(text, convert_to_tensor=False).tolist()
    embeddings.append(vector)

# Batch insert for speed
collection.add(
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)

print(f"🎉 SUCCESS! {len(chunks)} new legal chunks injected into Law-GPT.")
