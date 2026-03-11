import os
import sys
import json
import chromadb
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pypdf
from rank_bm25 import BM25Okapi
import pickle
import string
import shutil
from pathlib import Path

# Fix the path so it can always find your config.py file
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# THE MISSING IMPORTS:
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
        print(f"❌ Error reading {pdf_path}: {e}")
        return ""

def load_documents():
    documents = []
    # 1. Load BNS 2023 PDF (CRITICAL)
    bns_path = Path(DATA_DIR) / "BNS_2023.pdf"
    if bns_path.exists():
        print("📖 Loading BNS 2023 PDF...")
        text = extract_text_from_pdf(bns_path)
        documents.append({
            "text": text,
            "source": "Bharatiya Nyaya Sanhita (BNS) 2023",
            "title": "BNS 2023 Statutory Text"
        })
    else:
        print(f"⚠️ BNS 2023 PDF not found at {bns_path}")

    return documents

def main():
    print("🚀 Starting Unified Ingestion Pipeline...")

    # 1. THE HARD NUKE: Physically delete the folder to kill corruption at the root
    if os.path.exists(CHROMA_DB_PATH):
        print(f"🗑️ Physically deleting old ChromaDB folder to prevent corruption...")
        try:
            shutil.rmtree(CHROMA_DB_PATH)
            import time
            time.sleep(2) # Give Arch Linux a moment to release file locks
        except Exception as e:
            print(f"⚠️ Could not physically delete folder: {e}")

    # Ensure directory exists fresh
    os.makedirs(os.path.dirname(CHROMA_DB_PATH), exist_ok=True)

    # 2. Initialize fresh client
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

    # 3. SAFER CREATION: Use get_or_create instead of just create
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    print(f"🧠 Loading Embedding Model on GPU...")
    # Using CUDA to ensure your RTX 3050 processes this fast
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cuda")

    raw_docs = load_documents()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    print("✂️ Chunking documents...")
    chunked_docs = []
    chunk_metadatas = []
    chunk_ids = []

    doc_count = 0
    for doc in raw_docs:
        chunks = text_splitter.split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunked_docs.append(chunk)

            chunk_metadatas.append({
                "source": doc["source"],
                "title": doc.get("title", "Unknown")
            })
            chunk_ids.append(f"doc_{doc_count}_chunk_{i}")
        doc_count += 1

    print(f"📦 Prepared {len(chunked_docs)} text chunks. Saving to ChromaDB...")

    # INGESTION LOOP
    for i in tqdm(range(0, len(chunked_docs), INGEST_BATCH_SIZE), desc="Ingesting Vector DB"):
        batch_end = i + INGEST_BATCH_SIZE
        batch_text = chunked_docs[i:batch_end]
        batch_meta = chunk_metadatas[i:batch_end]
        batch_ids = chunk_ids[i:batch_end]

        embeddings = embedding_model.encode(batch_text).tolist()
        collection.add(
            ids=batch_ids,
            embeddings=embeddings,
            documents=batch_text,
            metadatas=batch_meta
        )

    print("\n⚡ Building and Caching Lexical BM25 Index...")

    def tokenize(text):
        if not text: return []
        return text.lower().translate(str.maketrans('', '', string.punctuation)).split()

    if chunked_docs:
        tokenized_corpus = [tokenize(doc) for doc in tqdm(chunked_docs, desc="Tokenizing corpus")]
        bm25 = BM25Okapi(tokenized_corpus)

        # Delete old BM25 to prevent mismatches
        if os.path.exists(BM25_INDEX_PATH):
            os.remove(BM25_INDEX_PATH)

        with open(BM25_INDEX_PATH, "wb") as f:
            pickle.dump((bm25, chunked_docs, chunk_metadatas), f)
        print(f"✅ BM25 Index cached successfully at: {BM25_INDEX_PATH}")

if __name__ == "__main__":
    main()
