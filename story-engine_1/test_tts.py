"""Run: python test_tts.py"""
import os, google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# find SpeechConfig location
import google.generativeai as g
import inspect

# search all submodules
for name in dir(g):
    obj = getattr(g, name)
    if 'speech' in name.lower() or 'voice' in name.lower():
        print(f"genai.{name} = {obj}")

import google.generativeai.types as t
for name in dir(t):
    if 'speech' in name.lower() or 'voice' in name.lower() or 'audio' in name.lower():
        print(f"types.{name} = {getattr(t, name)}")

# try simple TTS without voice config
print("\n--- Simple TTS test ---")
m = genai.GenerativeModel("gemini-2.5-flash-preview-tts")
r = m.generate_content(
    "Say: Hello, this is a test.",
    generation_config={"response_mime_type": "audio/wav"}
)
c = r.candidates[0]
print(f"finish_reason: {c.finish_reason}")
if c.content and c.content.parts:
    for i, p in enumerate(c.content.parts):
        has_audio = hasattr(p, 'inline_data') and p.inline_data is not None
        print(f"part {i}: has_inline_data={has_audio}")
        if has_audio:
            print(f"  mime_type: {p.inline_data.mime_type}")
            print(f"  data_len: {len(p.inline_data.data)}")
            with open('/tmp/test_audio.wav', 'wb') as f:
                f.write(p.inline_data.data)
            print("  saved to /tmp/test_audio.wav")
