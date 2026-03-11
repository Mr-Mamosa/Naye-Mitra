import os
import sys
import time
import pandas as pd

# 1. Resolve Paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from engine import QueryEngine
except ImportError:
    print("❌ Error: Could not find engine.py.")
    sys.exit()

print("🚀 Loading Law-GPT Engine onto NVIDIA RTX 3050...")
engine = QueryEngine()

csv_path = os.path.join(current_dir, 'indian_law_benchmark.csv')
df = pd.read_csv(csv_path).head(10) # Test on 10 samples to be fast

latencies = []
print(f"\n🔬 Starting Test 3: Hardware Performance & Latency (10 Sample Queries)...")

for index, row in df.iterrows():
    q = row['Question']

    start_time = time.time()
    _ = engine.ask(q) # We just care about the time it takes, not the text output here
    end_time = time.time()

    duration = end_time - start_time
    latencies.append(duration)
    print(f"[{index+1}/10] Query processed in: {duration:.2f} seconds")

avg_latency = sum(latencies) / len(latencies)

print("\n" + "="*50)
print("📊 FINAL HARDWARE PERFORMANCE RESULTS")
print("="*50)
print(f"CPU Processing  : AMD Ryzen 5 6600H")
print(f"GPU Processing  : NVIDIA RTX 3050 (6GB VRAM)")
print(f"Average Latency : {avg_latency:.2f} seconds per query")
print(f"Max Latency     : {max(latencies):.2f} seconds")
print(f"Min Latency     : {min(latencies):.2f} seconds")
print("="*50)

# Save to CSV for your graphs
results_df = pd.DataFrame({"Query_Number": range(1, 11), "Latency_Seconds": latencies})
output_path = os.path.join(current_dir, 'test3_performance_results.csv')
results_df.to_csv(output_path, index=False)
print(f"💾 Latency results saved to {output_path}")
