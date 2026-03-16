"""
Run this to diagnose the safety issue:
  python test.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

api_key = os.environ.get("GEMINI_API_KEY")
print(f"Key: {api_key[:8]}...")
genai.configure(api_key=api_key)

safety = [
    {"category": HarmCategory.HARM_CATEGORY_HARASSMENT,        "threshold": HarmBlockThreshold.BLOCK_NONE},
    {"category": HarmCategory.HARM_CATEGORY_HATE_SPEECH,       "threshold": HarmBlockThreshold.BLOCK_NONE},
    {"category": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT, "threshold": HarmBlockThreshold.BLOCK_ONLY_HIGH},
    {"category": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT, "threshold": HarmBlockThreshold.BLOCK_NONE},
]

model = genai.GenerativeModel("gemini-2.5-flash", safety_settings=safety)

print("\n--- Test 1: hello ---")
r = model.generate_content("Say hello.")
c = r.candidates[0]
print(f"finish_reason: {c.finish_reason}")
print(f"text: {r.text[:100]}")

print("\n--- Test 2: story seed ---")
r2 = model.generate_content(
    "You are a story architect. Seed: a lighthouse keeper finds a mystery. "
    "Return JSON with core_identity and theme only. ONLY valid JSON."
)
c2 = r2.candidates[0]
print(f"finish_reason: {c2.finish_reason}")
print(f"safety_ratings: {[(x.category.name, x.probability.name) for x in c2.safety_ratings]}")
print(f"prompt_feedback: {r2.prompt_feedback}")
try:
    print(f"text: {r2.text[:300]}")
except Exception as e:
    print(f"text error: {e}")
