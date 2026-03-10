import os
import pandas as pd
from engine import QueryEngine # Adjust this import if your file name is different
from ablation_logic import run_retrieval_comparison

# 1. Setup
engine = QueryEngine()
script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, 'indian_law_benchmark.csv')

# 2. Load Questions and Ground Truth
df = pd.read_csv(input_file)
# Assuming your CSV has columns: 'Question' and 'BNS_Section_Number'
questions = df['Question'].tolist()
targets = df['BNS_Ground_Truth (Your System)'].tolist()

# 3. Run Test
print("🚀 Starting Ablation Study: Vector vs. Hybrid Retrieval...")
results_df = run_retrieval_comparison(engine, questions, targets)

# 4. Save for Graphing
output_path = os.path.join(script_dir, 'ablation_results.csv')
results_df.to_csv(output_path, index=False)

# 5. Print Final Stats for your Paper
v_acc = (results_df['Vector_Only_Hit'].sum() / len(df)) * 100
h_acc = (results_df['Hybrid_Hit'].sum() / len(df)) * 100

print(f"\n--- ABLATION RESULTS ---")
print(f"Vector-Only Retrieval Recall@5: {v_acc}%")
print(f"Hybrid Retrieval Recall@5: {h_acc}%")
print(f"Improvement: {h_acc - v_acc}%")
print(f"Data saved to {output_path}")
