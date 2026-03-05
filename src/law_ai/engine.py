import time
import torch
import json
import numpy as np
import os
import pickle
import string
from sklearn.metrics.pairwise import cosine_similarity
from langchain_classic.memory import ConversationBufferWindowMemory
from sentence_transformers import SentenceTransformer, CrossEncoder
from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import chromadb

# --- NEW: Added get_case_history to the imports ---
from logger import init_db, log_interaction, get_case_history
from config import (
    CHROMA_DB_PATH,
    MODEL_PATH,
    EMBEDDING_MODEL_NAME,
    CROSS_ENCODER_MODEL_NAME,
    COLLECTION_NAME,
    BM25_INDEX_PATH,
    LLM_N_GPU_LAYERS,
    LLM_N_BATCH,
    LLM_N_CTX,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_STOP_WORDS,
    RAG_N_RESULTS,
    RERANK_TOP_N
)


class QueryEngine:
    def __init__(self):
        print(f"🚀 Initializing Law-GPT Engine...")

        # Initialize the Audit Trail Database
        init_db()
        print("📊 Audit Telemetry Database Initialized.")

        print("🧠 Loading Cross-Encoder Re-ranker...")
        self.reranker = CrossEncoder(CROSS_ENCODER_MODEL_NAME, device='cpu')

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"❌ Model file NOT found at: {MODEL_PATH}")
        print(f"📂 Model detected at: {MODEL_PATH}")

        self.client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        self.collection = self.client.get_collection(name=COLLECTION_NAME)

        # --- PHASE 5: HYBRID SEARCH (LOAD PRE-BUILT BM25 INDEX) ---
        print("⚡ Loading Lexical BM25 Index for Hybrid Search...")
        self.bm25 = None
        self.all_documents = []
        self.all_metadatas = []

        if os.path.exists(BM25_INDEX_PATH):
            try:
                with open(BM25_INDEX_PATH, "rb") as f:
                    self.bm25 = pickle.load(f)

                all_data = self.collection.get(include=['documents', 'metadatas'])
                self.all_documents = all_data.get('documents', [])
                self.all_metadatas = all_data.get('metadatas', [])

                print(f"✅ BM25 Index loaded with {len(self.all_documents)} documents.")
            except Exception as e:
                print(f"⚠️ BM25 Index loading failed: {e}. Lexical search will be disabled.")
                self.bm25 = None
        else:
            print("⚠️ BM25 Index not found. Run ingestion to build it. Lexical search disabled.")

        print("🧠 Loading embedding model on GPU (CUDA)...")
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device='cuda')

        gpu_layers = LLM_N_GPU_LAYERS if torch.cuda.is_available() else 0
        print(f"✅ GPU Mode: Offloading {gpu_layers} layers to GPU")

        try:
            self.llm = LlamaCpp(
                model_path=MODEL_PATH,
                n_gpu_layers=gpu_layers,
                n_batch=LLM_N_BATCH,
                n_ctx=LLM_N_CTX,
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                stop=LLM_STOP_WORDS,
                verbose=False,
            )
        except Exception as e:
            print(f"❌ LlamaCpp Failed: {e}")
            raise

        # We keep this for transform_query compatibility, though we now fetch history from DB
        self.memory = ConversationBufferWindowMemory(
            k=2,
            memory_key="chat_history",
            human_prefix="User",
            ai_prefix="Assistant"
        )

        # PHASE 3 UPGRADE: The Formal IRAC Prompt
        # PHASE 3 UPGRADE: Adaptive Formatting Prompt
        self.prompt_string = (
            "<|start_header_id|>system<|end_header_id|>\n\n"
            "You are 'Law-GPT', an elite AI Legal Consultant for Indian Law.\n"
            "CRITICAL RULES:\n"
            "1. You MUST ONLY use the facts and laws explicitly written in the CONTEXT below.\n"
            "2. IF THE CONTEXT DOES NOT CONTAIN THE EXACT TEXT OF A LAW, DO NOT INVENT IT. State 'The specific text is not in the retrieved documents.'\n"
            "3. NEVER hallucinate section numbers or case names.\n\n"
            "FORMATTING INSTRUCTIONS:\n"
            "- Adapt your response format to the user's specific request. If they ask for a simple summary, give a short summary. If they ask for bullet points, use them.\n"
            "- If the user presents a complex case scenario without specifying a format, break down your answer logically (e.g., Identify the law, apply it to the facts, and conclude).\n"
            "- ALWAYS answer naturally and professionally.\n\n"
            "CONTEXT:\n{context}\n\n"
            "PREVIOUS HISTORY:\n{chat_history}\n"
            "<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
            "CLIENT QUERY: {question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        self.rag_prompt = PromptTemplate(template=self.prompt_string)
        print("✅ Engine ready.")


    def retrieve_context(self, query_text: str, n_results=RAG_N_RESULTS):
        # 1. SEMANTIC SEARCH (ChromaDB Vector Search)
        query_embedding = self.embedding_model.encode(query_text, convert_to_tensor=False).tolist()
        vector_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )

        candidate_chunks = []
        candidate_metas = []

        if vector_results["documents"] and vector_results["documents"][0]:
            best_distance = vector_results["distances"][0][0]
            if best_distance <= 1.1:  # Guardrail check
                candidate_chunks.extend(vector_results["documents"][0])
                candidate_metas.extend(vector_results["metadatas"][0])

        # 2. LEXICAL SEARCH (BM25 Keyword Search)
        if self.bm25:
            tokenized_query = query_text.lower().translate(str.maketrans('', '', string.punctuation)).split()
            bm25_scores = self.bm25.get_scores(tokenized_query)

            top_bm25_indices = np.argsort(bm25_scores)[::-1][:n_results]

            for idx in top_bm25_indices:
                if bm25_scores[idx] > 0:
                    chunk = self.all_documents[idx]
                    meta = self.all_metadatas[idx]
                    if chunk not in candidate_chunks:
                        candidate_chunks.append(chunk)
                        candidate_metas.append(meta)

        # 3. FALLBACK CHECK
        if not candidate_chunks:
            return "NO_RELEVANT_LAW_FOUND", [], []

        # 4. THE ULTIMATE JUDGE (Cross-Encoder Re-Ranking)
        pairs = [[query_text, chunk] for chunk in candidate_chunks]
        scores = self.reranker.predict(pairs)

        ranked_indices = np.argsort(scores)[::-1]

        top_chunks = [candidate_chunks[i] for i in ranked_indices[:RERANK_TOP_N]]
        top_metas = [candidate_metas[i] for i in ranked_indices[:RERANK_TOP_N]]

        context = "\n\n---\n\n".join(top_chunks)
        sources = list({meta.get("source", "Unknown") for meta in top_metas})

        return context, sources, top_chunks

    def verify_credibility(self, generated_text, retrieved_chunks):
        if not generated_text or not retrieved_chunks:
            return 0, "Unknown"

        answer_vec = self.embedding_model.encode([generated_text])
        chunk_vecs = self.embedding_model.encode(retrieved_chunks)
        similarities = cosine_similarity(answer_vec, chunk_vecs)
        max_similarity = np.max(similarities)

        if max_similarity < 0.5:
            status = "🔴 HIGH RISK: Potential Hallucination"
        elif max_similarity < 0.7:
            status = "🟡 MEDIUM RISK: Verify Sources"
        else:
            status = "🟢 LOW RISK: Heavily Grounded in Sources"

        return round(float(max_similarity) * 100, 2), status

    # --- NEW: Updated ask function signature ---
    def ask(self, query_text: str, user_id: str = "anonymous", case_id: str = None, title: str = "New Case"):
        try:
            start_time = time.time()

            # --- NEW: Fetch stateful history for THIS specific case from SQLite ---
            history_str = get_case_history(case_id, limit=2)

            search_query = self.transform_query(query_text, history_str)

            context, sources, raw_chunks = self.retrieve_context(search_query)

            # Guardrail blocker
            if context == "NO_RELEVANT_LAW_FOUND":
                safe_answer = (
                    "This query involves parameters that fall outside the currently indexed jurisdictional databases (including the Bharatiya Nyaya Sanhita, IPC, and localized Supreme Court precedents). "
                    "In standard legal practice, matters lacking direct statutory overlap in the primary repositories require expanding the discovery scope or consulting domain-specific counsel. "
                    "Please provide additional jurisdictional context or rephrase the statutory constraints."
                )

                # --- NEW: Updated log_interaction call ---
                log_interaction(
                    query=query_text,
                    response=safe_answer,
                    sources=[],
                    confidence=0.0,
                    duration=0.0,
                    status="🔴 BLOCKED: Out of Scope",
                    user_id=user_id,
                    case_id=case_id,
                    title=title
                )
                return {
                    "answer": safe_answer,
                    "sources": [],
                    "time": 0.0,
                    "confidence": 0.0,
                    "status": "🔴 BLOCKED: Out of Scope",
                    "case_id": case_id
                }

            chain = self.rag_prompt | self.llm | StrOutputParser()
            full_response = ""

            for chunk in chain.stream({"context": context, "question": query_text, "chat_history": history_str}):
                full_response += chunk

            confidence, status = self.verify_credibility(full_response, raw_chunks)
            duration = round(time.time() - start_time, 2)

            # --- NEW: Updated log_interaction call with all variables ---
            log_interaction(
                query=query_text,
                response=full_response,
                sources=sources,
                confidence=confidence,
                duration=duration,
                status=status,
                user_id=user_id,
                case_id=case_id,
                title=title
            )

            # --- NEW: Added case_id to the return dict ---
            return {
                "answer": full_response,
                "sources": sources,
                "time": duration,
                "confidence": confidence,
                "status": status,
                "case_id": case_id
            }
        except Exception as e:
            return {"answer": f"Error: {str(e)}", "sources": [], "time": 0, "confidence": 0, "status": "Error", "case_id": case_id}

    def transform_query(self, user_query: str, history_str: str) -> str:
      """Uses the LLM to rewrite conversational queries into standalone legal queries."""
      if not history_str.strip():
          return user_query # No history to contextualize

      rewrite_prompt = (
          "<|start_header_id|>system<|end_header_id|>\n\n"
          "You are a legal search assistant. Read the chat history and the user's new question. "
          "Rewrite the user's question into a standalone, highly specific legal search query for a database. "
          "Do NOT answer the question. ONLY output the rewritten query.\n"
          "<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n"
          f"HISTORY: {history_str}\n"
          f"NEW QUESTION: {user_query}\n\n"
          "REWRITTEN QUERY:<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
      )

      rewritten = self.llm.invoke(rewrite_prompt, max_tokens=50, temperature=0.0)
      print(f"🔄 Query Transformed: '{user_query}' -> '{rewritten.strip()}'")
      return rewritten.strip()
