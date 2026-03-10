import os
import pandas as pd
import numpy as np

def run_retrieval_comparison(engine, questions, ground_truth_sections):
    """
    questions: List of strings (The 50 questions)
    ground_truth_sections: List of strings (The correct Section numbers, e.g., 'Section 318')
    """
    ablation_results = []

    for i, q in enumerate(questions):
        correct_sec = str(ground_truth_sections[i])

        # --- TEST 1: VECTOR ONLY ---
        # We simulate this by temporarily 'hiding' the BM25 index
        original_bm25 = engine.bm25
        engine.bm25 = None
        _, _, vector_chunks = engine.retrieve_context(q, n_results=5)

        # Check if the correct section number is in the top 5 chunks
        vector_hit = 1 if any(correct_sec.lower() in chunk.lower() for chunk in vector_chunks) else 0

        # --- TEST 2: HYBRID (BNS + BM25) ---
        engine.bm25 = original_bm25 # Restore BM25
        _, _, hybrid_chunks = engine.retrieve_context(q, n_results=5)

        # Check if correct section is in top 5 chunks
        hybrid_hit = 1 if any(correct_sec.lower() in chunk.lower() for chunk in hybrid_chunks) else 0

        ablation_results.append({
            "Question": q,
            "Target_Section": correct_sec,
            "Vector_Only_Hit": vector_hit,
            "Hybrid_Hit": hybrid_hit
        })
        print(f"Tested {i+1}/50: Vector:{vector_hit} | Hybrid:{hybrid_hit}")

    return pd.DataFrame(ablation_results)
