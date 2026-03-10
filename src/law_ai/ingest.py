import os
import json
import chromadb
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pypdf
from rank_bm25 import BM25Okapi
import pickle
import string
from pathlib import Path

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

    # # 2. Load the Cleaned Supreme Court Judgments (NEW)
    # json_path = Path(DATA_DIR) / "cleaned_judgments.json"
    # if json_path.exists():
    #     print(f"📖 Loading Cleaned SC Judgments from {json_path}...")
    #     try:
    #         with open(json_path, 'r', encoding='utf-8') as f:
    #             judgments = json.load(f)
    #             for j in judgments:
    #                 documents.append({
    #                     "text": j.get("text", ""),
    #                     "source": j.get("source", "Supreme Court Judgment"),
    #                     "title": j.get("title", "Unknown Case")
    #                 })
    #         print(f"✅ Successfully loaded {len(judgments)} SC Headnotes.")
    #     except Exception as e:
    #         print(f"❌ Error loading JSON: {e}")
    # else:
    #     print(f"⚠️ Cleaned judgments JSON not found at {json_path}")

    return documents

def main():
    print("🚀 Starting Unified Ingestion Pipeline...")

    # Ensure directory exists
    os.makedirs(os.path.dirname(CHROMA_DB_PATH), exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))

    # Safely Reset
    try:
        client.delete_collection(COLLECTION_NAME)
        import time
        time.sleep(2) # CRITICAL: Wait for file system on Linux
        print("🗑️ Deleted old ChromaDB collection.")
    except Exception as e:
        print(f"ℹ️ No existing collection to delete or error: {e}")

    collection = client.create_collection(name=COLLECTION_NAME)

    print(f"🧠 Loading Embedding Model on GPU...")
    # Switched to CUDA for your RTX 3050
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cuda")

    raw_docs = load_documents()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )

    # ... [Rest of your chunking code is perfect] ...

    print("✂️ Chunking documents...")
    chunked_docs = []
    chunk_metadatas = []
    chunk_ids = []

    doc_count = 0
    for doc in raw_docs:
        chunks = text_splitter.split_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunked_docs.append(chunk)

            # Store source and title so the AI can cite it properly
            chunk_metadatas.append({
                "source": doc["source"],
                "title": doc.get("title", "Unknown")
            })
            chunk_ids.append(f"doc_{doc_count}_chunk_{i}")
        doc_count += 1

    print(f"📦 Prepared {len(chunked_docs)} text chunks. Saving to ChromaDB...")

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

        # Save the BM25 index and the raw chunks/metadatas!
        with open(BM25_INDEX_PATH, "wb") as f:
            pickle.dump((bm25, chunked_docs, chunk_metadatas), f)
        print(f"✅ BM25 Index cached successfully at: {BM25_INDEX_PATH}")

if __name__ == "__main__":
    main()
