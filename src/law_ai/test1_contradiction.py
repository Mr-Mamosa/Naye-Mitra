import os
import sys
import time
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from engine import QueryEngine
except ImportError:
    print("❌ Error: Could not find engine.py.")
    sys.exit()

print("🚀 Loading Law-GPT Engine onto GPU...")
engine = QueryEngine()

# 3 Trick Questions: Old IPC vs New BNS
# e.g., Sedition was 124A IPC, now acts endangering sovereignty are 152 BNS.
# Snatching wasn't explicitly defined in IPC, but is Section 304 in BNS.
trick_questions = [
    "What is the specific section and punishment for acts endangering the sovereignty, unity and integrity of India?",
    "Under what section is the specific crime of 'Snatching' defined and penalized?",
    "A person promises to marry a woman deceitfully to have consensual sex. What section penalizes this?"
]

results = []

print("\n🔬 Starting Test 1: Temporal Contradiction (BNS strictness)...")

for i, q in enumerate(trick_questions):
    print(f"\nProcessing Question {i+1}/3...")
    start_time = time.time()

    # We use the full Hybrid pipeline
    answer = engine.ask(q)

    elapsed = time.time() - start_time
    print(f"Time: {elapsed:.2f}s")
    print(f"Q: {q}")
    print(f"Law-GPT Answer: {answer}\n")
    print("-" * 50)

    results.append({
        "Question": q,
        "LawGPT_Answer": answer,
        "Latency_Seconds": round(elapsed, 2)
    })

# Save the evidence for the paper
df = pd.DataFrame(results)
output_path = os.path.join(current_dir, 'test1_contradiction_results.csv')
df.to_csv(output_path, index=False)
print(f"💾 Contradiction test evidence saved to {output_path}")
