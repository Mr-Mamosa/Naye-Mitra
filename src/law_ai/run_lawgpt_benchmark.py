import os
import pandas as pd
from google import genai
from google.genai import errors
import time

# 1. Setup (Use a NEW key if possible!)
client = genai.Client(api_key="AIzaSyCRJAhQMfQNONg7U6Z438ePj5zye0Te8bg")

script_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(script_dir, 'indian_law_benchmark.csv')
output_file = os.path.join(script_dir, 'benchmark_results_gemini.csv')

df = pd.read_csv(input_file)

# If a partial result exists, load it to resume (Optional)
if os.path.exists(output_file):
    results_df = pd.read_csv(output_file)
    results = results_df['Gemini_Output'].tolist()
    start_idx = len(results)
else:
    results = []
    start_idx = 0

print(f"🚀 Starting/Resuming Gemini Benchmark at question {start_idx + 1}...")

# 2. Execution Loop
for index in range(start_idx, len(df)):
    question = df.iloc[index]['Question']
    success = False
    attempts = 0

    while not success and attempts < 5:
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash', # Using 2.0 Flash (Fastest/highest quota)
                contents=question
            )

            answer = response.text if response.text else "NO_RESPONSE_TEXT"
            results.append(answer)
            print(f"[{index + 1}/{len(df)}] ✅ Success")
            success = True

            # 6 second sleep to stay safely under 10 RPM (Free Tier safe zone)
            time.sleep(6)

        except errors.APIError as e:
            if e.code == 429:
                wait_time = 60 # If we hit a wall, wait a full minute
                print(f"[{index + 1}/{len(df)}] ⚠️ Rate limit wall. Sleeping {wait_time}s...")
                time.sleep(wait_time)
                attempts += 1
            else:
                print(f"[{index + 1}/{len(df)}] ❌ API Error {e.code}. Skipping.")
                results.append(f"API_ERROR_{e.code}")
                success = True
        except Exception as e:
            print(f"[{index + 1}/{len(df)}] ❌ Unknown error. Skipping.")
            results.append(f"ERROR: {e}")
            success = True

    # 3. SAVE PROGRESS EVERY 5 STEPS (So you don't lose data!)
    if (index + 1) % 5 == 0 or (index + 1) == len(df):
        temp_df = df.iloc[:len(results)].copy()
        temp_df['Gemini_Output'] = results
        temp_df.to_csv(output_file, index=False)
        print(f"💾 Progress saved to {output_file}")

print(f"\n✨ DONE! Final results saved to: {output_file}")
