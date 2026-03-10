import time
import torch
import pandas as pd
import os
import sys

# 1. RESOLVE MODULE PATH
# This adds the 'src/law_ai' directory to the Python path so it can find engine.py
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from engine import QueryEngine
except ImportError:
    # Fallback if you are running this from the root of the project
    from src.law_ai.engine import QueryEngine

# 2. RESOLVE DATA PATH
# This ensures the CSV is found even if you run the script from the project root
csv_path = os.path.join(current_dir, 'indian_law_benchmark.csv')

if not os.path.exists(csv_path):
    print(f"❌ Error: Could not find CSV at {csv_path}")
    sys.exit(1)

# 3. INITIALIZE ENGINE
engine = QueryEngine()
df = pd.read_csv(csv_path).head(10) # Test on 10 samples
latencies = []

print("🚀 Starting Latency Benchmark...")
# (Rest of your loop remains the same)
for q in df['Question']:
    start = time.time()
    _ = engine.ask(q)
    end = time.time()

    duration = end - start
    latencies.append(duration)
    print(f"Query took: {duration:.2f}s")

avg_latency = sum(latencies) / len(latencies)
print(f"\n--- PERFORMANCE RESULTS ---")
print(f"Average Response Time: {avg_latency:.2f} seconds")
print(f"Hardware: NVIDIA RTX 3050 6GB")
