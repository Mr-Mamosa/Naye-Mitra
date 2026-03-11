import os
import sys
import pandas as pd
import time

# 1. Resolve Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# 2. Import your local Engine
try:
    from engine import QueryEngine
except ImportError:
    print("❌ Error: Could not find engine.py. Make sure this script is in the same folder!")
    sys.exit()

# 3. Initialize
print("🚀 Loading Law-GPT Engine onto GPU...")
engine = QueryEngine()

# Connect the CSV Database
csv_path = os.path.join(current_dir, 'indian_law_benchmark.csv')
if not os.path.exists(csv_path):
    print(f"❌ Error: CSV not found at {csv_path}")
    sys.exit()

df = pd.read_csv(csv_path)
results = []

print(f"🔬 Starting Ablation Test (Vector vs. Hybrid) for {len(df)} questions...")

# 4. Execution Loop
for index, row in df.iterrows():
    q = row['Question']

    # Matches your exact CSV column and extracts just the section number (e.g., "318")
    raw_target = str(row['BNS_Ground_Truth (Your System)'])
    target_sec = "".join(filter(str.isdigit, raw_target))

    # --- STEP A: VECTOR-ONLY RETRIEVAL ---
    original_bm25 = engine.bm25
    engine.bm25 = None
    _, _, vector_chunks = engine.retrieve_context(q, n_results=5)

    # Context Merging: Joins top 5 chunks into one string so split numbers don't fail
    all_v_text = " ".join(vector_chunks).lower()
    v_hit = 1 if target_sec in all_v_text else 0

    # --- STEP B: HYBRID RETRIEVAL (Vector + BM25) ---
    engine.bm25 = original_bm25
    _, _, hybrid_chunks = engine.retrieve_context(q, n_results=5)

    all_h_text = " ".join(hybrid_chunks).lower()
    h_hit = 1 if target_sec in all_h_text else 0

    results.append({"Vector_Hit": v_hit, "Hybrid_Hit": h_hit})
    print(f"[{index+1}/50] Target: {target_sec} | Vector: {v_hit} | Hybrid: {h_hit}")

# 5. Save and Output Analytics
results_df = pd.DataFrame(results)
v_acc = (results_df['Vector_Hit'].sum() / len(df)) * 100
h_acc = (results_df['Hybrid_Hit'].sum() / len(df)) * 100

print(f"\n--- FINAL RESULTS FOR TEST 2 ---")
print(f"Vector-Only Accuracy: {v_acc:.2f}%")
print(f"Hybrid-Search Accuracy: {h_acc:.2f}%")
print(f"Improvement: {h_acc - v_acc:.2f}%")

# Generate the results CSV for your thesis graphs
final_df = pd.concat([df, results_df], axis=1)
output_file = os.path.join(current_dir, 'test2_ablation_results.csv')
final_df.to_csv(output_file, index=False)
print(f"💾 Results successfully saved to {output_file}")
