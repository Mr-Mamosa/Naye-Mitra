import json
import time
import re
from pathlib import Path
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb

# --- Configuration ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CHROMA_DB_PATH = PROJECT_ROOT / "data" / "chroma_db"
JSONL_PATH = PROJECT_ROOT / "data" / "sc_judgments_text.jsonl"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "legal_kb"

BATCH_SIZE = 50 # Lowered slightly to handle metadata overhead
MAX_LINES_TO_PROCESS = 5000

def stream_jsonl(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            yield json.loads(line)

def build_json_database():
    print("⚖️ Initializing Advanced Legal Ingestor...")

    if not JSONL_PATH.exists():
        print(f"❌ File not found: {JSONL_PATH}")
        return

    print("🧠 Loading embedding model on GPU (CUDA)...")
    embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device='cuda')

    print("🗄️ Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    # LEGAL SPLITTER: Prioritizes paragraphs and legal markers
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n\n", "Held:", "Judgment:", "Conclusion:", "\n", ".", " "]
    )

    print("🔍 Scanning existing database...")
    existing_ids = set(collection.get(include=[])['ids'])

    batch_texts, batch_metadatas, batch_ids = [], [], []
    total_chunks_saved = 0
    line_count = 0
    skipped_count = 0
    start_time = time.time()

    try:
        for item in stream_jsonl(JSONL_PATH):
            if line_count >= MAX_LINES_TO_PROCESS:
                break
            line_count += 1
            line_id_prefix = f"sc_case_{line_count}"

            if f"{line_id_prefix}_chunk0" in existing_ids:
                skipped_count += 1
                continue

            raw_text = item.get("text", "") or item.get("content", "")
            # ADVANCED: Extract Year and Case Name from the title if possible
            title = item.get("title", f"SC Judgment {line_count}")
            year_match = re.search(r'\b(19|20)\d{2}\b', title)
            year = year_match.group(0) if year_match else "Unknown"

            if not raw_text:
                continue

            chunks = text_splitter.split_text(raw_text)

            for i, chunk_text in enumerate(chunks):
                # We prefix the chunk with the Case Name so the LLM always knows what it's reading
                context_aware_text = f"CASE: {title}\nYEAR: {year}\nCONTENT: {chunk_text}"

                batch_texts.append(context_aware_text)
                batch_metadatas.append({
                    "source": title,
                    "type": "Precedent",
                    "year": year
                })
                batch_ids.append(f"{line_id_prefix}_chunk{i}")

            if len(batch_texts) >= BATCH_SIZE:
                embeddings = embedding_model.encode(batch_texts, convert_to_tensor=False).tolist()
                collection.add(
                    documents=batch_texts,
                    embeddings=embeddings,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                total_chunks_saved += len(batch_texts)
                print(f"⚡ Ingesting... Lines Skipped: {skipped_count} | New Chunks: {total_chunks_saved}", end="\r")
                batch_texts, batch_metadatas, batch_ids = [], [], []

        if batch_texts:
            embeddings = embedding_model.encode(batch_texts, convert_to_tensor=False).tolist()
            collection.add(documents=batch_texts, embeddings=embeddings, metadatas=batch_metadatas, ids=batch_ids)
            total_chunks_saved += len(batch_texts)

        elapsed = round((time.time() - start_time) / 60, 2)
        print(f"\n\n🎉 Done! {total_chunks_saved} chunks indexed in {elapsed} mins.")

    except Exception as e:
        print(f"\n❌ Error during ingestion: {e}")

if __name__ == "__main__":
    build_json_database()
