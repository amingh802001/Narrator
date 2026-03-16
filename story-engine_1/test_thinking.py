"""
Run this to find the right way to disable thinking:
  python test_thinking.py
"""
import os, inspect
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# print SDK version
import google.generativeai as g
print(f"SDK version: {g.__version__}")

# print GenerationConfig fields
from google.generativeai.types import GenerationConfig
print(f"\nGenerationConfig fields:")
print(inspect.signature(GenerationConfig.__init__))

# try generate_content signature
m = genai.GenerativeModel("gemini-2.5-flash")
print(f"\ngenerate_content signature:")
print(inspect.signature(m.generate_content))

# test basic call
print("\n--- Basic test ---")
r = m.generate_content("Reply with one word: hello")
try:
    print(f"text: {r.text}")
except Exception as e:
    print(f"text error: {e}")
    print(f"candidates: {r.candidates}")
    if r.candidates:
        c = r.candidates[0]
        print(f"finish_reason: {c.finish_reason}")
        print(f"parts: {c.content.parts if c.content else 'none'}")
