from engine import QueryEngine

engine = QueryEngine()

# Let's check a specific case: Conspiracy (Section 61)
test_q = "Two or more people agree to commit an illegal act. What section defines this criminal conspiracy?"
context, sources, chunks = engine.retrieve_context(test_q, n_results=3)

print("\n--- DEBUG START ---")
print(f"Question: {test_q}")
print(f"Top Source found: {sources[0] if sources else 'NONE'}")
print(f"First 100 chars of Chunk 1: {chunks[0][:100] if chunks else 'EMPTY'}")
print("--- DEBUG END ---\n")
