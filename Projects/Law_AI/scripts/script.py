from pathlib import Path
from llama_cpp import Llama

model_path = Path("/home/adnan/Projects/Law AI/data/models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf")

llm = Llama(
    model_path=str(model_path),
    n_gpu_layers=32,
    n_ctx=2048,
    verbose=True,  # Turn on verbose to see what's happening
)

# Test 1: Plain prompt (no special tokens)
print("=== TEST 1: PLAIN PROMPT ===")
output = llm("The capital of France is", max_tokens=20, stop=["\n"])
print(output["choices"][0]["text"])

# Test 2: Chat format
print("\n=== TEST 2: CHAT FORMAT ===")
output2 = llm.create_chat_completion(
    messages=[{"role": "user", "content": "What is 2+2? Answer in one word."}],
    max_tokens=20,
)
print(output2["choices"][0]["message"]["content"])
