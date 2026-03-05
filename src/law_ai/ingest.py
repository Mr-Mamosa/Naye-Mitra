import json
import chromadb
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pypdf
from rank_bm25 import BM25Okapi
import pickle
import string

from config import (
    DATA_DIR,
    CHROMA_DB_PATH,
    EMBEDDING_MODEL_NAME,
    COLLECTION_NAME,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    INGEST_BATCH_SIZE,
    BM25_INDEX_PATH
)

def extract_text_from_pdf(pdf_path):
    """Extracts text from a single PDF."""
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
        return ""

def load_documents():
    documents = []

    # 1. Load IPC text file (faster than PDF)
    ipc_path = DATA_DIR / "ipc_text.txt"
    if ipc_path.exists():
        print("📖 Loading IPC text...")
        text = ipc_path.read_text(encoding="utf-8")
        documents.append({"text": text, "source": "Indian Penal Code (IPC)"})

    # 2. Load pre-extracted judgments from JSONL
    jsonl_path = DATA_DIR / "sc_judgments_text.jsonl"
    if jsonl_path.exists():
        print("📂 Loading SC judgments from JSONL...")
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in tqdm(f, desc="Reading judgments"):
                record = json.loads(line)
                text = record.get("text", "") or record.get("content", "")
                source = record.get("filename", record.get("source", "SC Judgment"))
                if len(text) > 100:
                    documents.append({"text": text, "source": f"Supreme Court Judgment: {source}"})

    return documents

def main():
    print("🚀 Starting Ingestion Pipeline...")

    # 1. Initialize Database
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

    # Reset collection (Clean Slate)
    try:
        client.delete_collection(COLLECTION_NAME)
        print("🗑️  Deleted old collection to ensure fresh start.")
    except Exception:
        pass

    collection = client.create_collection(name=COLLECTION_NAME)

    # 2. Load Embeddings Model (CPU is fine for ingestion)
    print(f"🧠 Loading Embedding Model ({EMBEDDING_MODEL_NAME})...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cuda")

    # 3. Load & Split Data
    raw_docs = load_documents()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    print("✂️  Chunking documents...")
    chunked_docs = []
    chunk_metadatas = []
    chunk_ids = []

    doc_count = 0
    for doc in raw_docs:
        chunks = text_splitter.split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunked_docs.append(chunk)
            chunk_metadatas.append({"source": doc["source"]})
            chunk_ids.append(f"doc_{doc_count}_chunk_{i}")
        doc_count += 1

    print(f"📦 Prepared {len(chunked_docs)} text chunks for embedding.")

    # 4. Insert into ChromaDB (Batched)
    print("💾 Saving to ChromaDB...")
    for i in tqdm(range(0, len(chunked_docs), INGEST_BATCH_SIZE), desc="Ingesting"):
        batch_end = i + INGEST_BATCH_SIZE
        batch_text = chunked_docs[i:batch_end]
        batch_meta = chunk_metadatas[i:batch_end]
        batch_ids = chunk_ids[i:batch_end]

        # Embed
        embeddings = embedding_model.encode(batch_text).tolist()

        # Upsert
        collection.add(
            ids=batch_ids,
            embeddings=embeddings,
            documents=batch_text,
            metadatas=batch_meta
        )

    print(f"\n✅ Success! Database built at: {CHROMA_DB_PATH}")

    # --- PHASE 5: POST-INGESTION: BUILD AND CACHE BM25 INDEX ---
    print("\n⚡ Building and Caching Lexical BM25 Index...")

    def tokenize(text):
        if not text:
            return []
        return text.lower().translate(str.maketrans('', '', string.punctuation)).split()

    all_docs = collection.get(include=['documents'])
    all_documents_text = all_docs['documents']

    if all_documents_text:
        tokenized_corpus = [tokenize(doc) for doc in tqdm(all_documents_text, desc="Tokenizing corpus")]
        bm25 = BM25Okapi(tokenized_corpus)
        
        with open(BM25_INDEX_PATH, "wb") as f:
            pickle.dump(bm25, f)
        print(f"✅ BM25 Index cached successfully at: {BM25_INDEX_PATH}")
    else:
        print("⚠️ No documents found to build BM25 index.")

if __name__ == "__main__":
    main()
