"""Run: python test_image.py"""
import os, base64, google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

model = genai.GenerativeModel("gemini-2.5-flash-image")
print("Testing image generation...")

response = model.generate_content(
    "A lighthouse on a rocky coast at dusk, dramatic clouds, cinematic photography style."
)

for candidate in response.candidates:
    if candidate.content and candidate.content.parts:
        for part in candidate.content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                data = part.inline_data.data
                with open('/tmp/test_scene.png', 'wb') as f:
                    f.write(data)
                print(f"Success! Image saved ({len(data)} bytes)")
            elif hasattr(part, 'text') and part.text:
                print(f"Text response: {part.text[:100]}")
