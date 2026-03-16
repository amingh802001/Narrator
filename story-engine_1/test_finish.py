"""Run: python test_finish.py"""
import os, google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

m = genai.GenerativeModel("gemini-2.5-flash")

prompt = """You are a story architect. Given a seed idea, extract the story's essential identity.

Seed idea: A lighthouse keeper discovers the light has been warning ships away from something that wants to be found

Return a JSON object:
{
  "core_identity": "one sentence",
  "emotional_signature": "how it feels",
  "central_want_pain": "engine",
  "theme": "theme",
  "genre_hint": "genre",
  "world_contract": {"ethos": "x", "norms": "x", "enforcement": "x", "world_gap": "x"},
  "protagonist": {"name": "x", "background": "x", "core_gap": "x", "values": "x", "surface_want": "x", "deeper_need": "x"}
}

Return ONLY valid JSON."""

r = m.generate_content(prompt)
c = r.candidates[0]
print(f"finish_reason value: {c.finish_reason}")
print(f"finish_reason type: {type(c.finish_reason)}")
print(f"parts count: {len(c.content.parts) if c.content else 0}")
if c.content and c.content.parts:
    for i, p in enumerate(c.content.parts):
        thought = getattr(p, 'thought', False)
        text_len = len(p.text) if hasattr(p, 'text') and p.text else 0
        print(f"  part {i}: thought={thought}, text_len={text_len}")
        if text_len > 0:
            print(f"  preview: {p.text[:100]}")
try:
    print(f"\nresponse.text: {r.text[:200]}")
except Exception as e:
    print(f"\nresponse.text error: {e}")
