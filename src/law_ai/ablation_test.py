import os
import sys
import pandas as pd
import time

# 1. FIX THE PATHS (This ensures it finds your engine.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 2. IMPORT YOUR ENGINE (Check: Is your file named 'engine.py'?)
try:
    from engine import QueryEngine
except ImportError:
    print("❌ Error: Could not find engine.py. Make sure this script is in the same folder!")
    sys.exit()

# 3. INITIALIZE
print("🚀 Loading Law-GPT Engine onto GPU...")
engine = QueryEngine()

# Path to your benchmark file
csv_path = os.path.join(current_dir, 'indian_law_benchmark.csv')
df = pd.read_csv(csv_path)

results = []

print(f"🔬 Starting Ablation Test (Vector vs. Hybrid) for {len(df)} questions...")

# 4. EXECUTION LOOP
for index, row in df.iterrows():
    q = row['Question']
    target_sec = str(row['BNS_Section_Number']) # Make sure this matches your CSV column!

    # --- STEP A: VECTOR-ONLY RETRIEVAL ---
    # We disable BM25 temporarily
    original_bm25 = engine.bm25
    engine.bm25 = None
    _, _, vector_chunks = engine.retrieve_context(q, n_results=5)

    # Check for a "Hit" (if the section number is in any of the top 5 chunks)
    v_hit = 1 if any(target_sec in chunk for chunk in vector_chunks) else 0

    # --- STEP B: HYBRID RETRIEVAL ---
    # We re-enable BM25
    engine.bm25 = original_bm25
    _, _, hybrid_chunks = engine.retrieve_context(q, n_results=5)

    h_hit = 1 if any(target_sec in chunk for chunk in hybrid_chunks) else 0

    results.append({"Vector_Hit": v_hit, "Hybrid_Hit": h_hit})
    print(f"[{index+1}/50] Target: {target_sec} | Vector: {v_hit} | Hybrid: {h_hit}")

# 5. SAVE AND ANALYZE
results_df = pd.DataFrame(results)
v_acc = (results_df['Vector_Hit'].sum() / len(df)) * 100
h_acc = (results_df['Hybrid_Hit'].sum() / len(df)) * 100

print(f"\n--- FINAL RESULTS FOR TEST 2 ---")
print(f"Vector-Only Accuracy: {v_acc}%")
print(f"Hybrid-Search Accuracy: {h_acc}%")
print(f"Improvement: {h_acc - v_acc}%")

# Save to CSV for your graphs
final_df = pd.concat([df, results_df], axis=1)
final_df.to_csv(os.path.join(current_dir, 'test2_ablation_results.csv'), index=False)
