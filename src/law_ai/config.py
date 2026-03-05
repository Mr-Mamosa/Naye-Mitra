from pathlib import Path

# --- Path Configuration ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DB_PATH = str(DATA_DIR / "chroma_db")
BM25_INDEX_PATH = str(DATA_DIR / "bm25_index.pkl")
MODEL_PATH = str(DATA_DIR / "models" / "Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf")


# --- Model Configuration ---
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL_NAME = 'cross-encoder/ms-marco-MiniLM-L-6-v2'


# --- RAG Configuration ---
COLLECTION_NAME = "legal_kb"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RAG_N_RESULTS = 10
RERANK_TOP_N = 5


# --- LLM Configuration ---
LLM_N_GPU_LAYERS = 34 # Number of layers to offload to GPU
LLM_N_BATCH = 512
LLM_N_CTX = 4096
LLM_TEMPERATURE = 0.0
LLM_MAX_TOKENS = 2048
LLM_STOP_WORDS = ["<|eot_id|>", "<|end_of_text|>", "User:", "… … …"]


# --- Ingestion Configuration ---
INGEST_BATCH_SIZE = 128
