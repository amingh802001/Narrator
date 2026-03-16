"""Run: python test_tts_v2.py"""
import os, google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# find where SpeechConfig lives
import google.ai.generativelanguage as glm
print("Searching for SpeechConfig...")
for name in dir(glm):
    if 'speech' in name.lower() or 'voice' in name.lower():
        print(f"  glm.{name}")

# try direct proto approach
print("\n--- TTS test with proto config ---")
try:
    from google.ai.generativelanguage_v1beta.types import (
        SpeechConfig, VoiceConfig, PrebuiltVoiceConfig
    )
    print("Found SpeechConfig in v1beta types")

    model = genai.GenerativeModel("gemini-2.5-flash-preview-tts")
    speech_config = SpeechConfig(
        voice_config=VoiceConfig(
            prebuilt_voice_config=PrebuiltVoiceConfig(voice_name="Charon")
        )
    )
    response = model.generate_content(
        "Say: Hello, this is Story Engine.",
        generation_config=genai.types.GenerationConfig(
            speech_config=speech_config
        )
    )
    print(f"finish_reason: {response.candidates[0].finish_reason}")
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            with open('/tmp/tts_test.wav', 'wb') as f:
                f.write(part.inline_data.data)
            print(f"Audio saved! {len(part.inline_data.data)} bytes")
except ImportError as e:
    print(f"Import error: {e}")
except Exception as e:
    print(f"Error: {e}")

# try passing speech_config as dict
print("\n--- TTS test with dict config ---")
try:
    model = genai.GenerativeModel("gemini-2.5-flash-preview-tts")
    response = model.generate_content(
        "Say: Hello, this is Story Engine.",
        generation_config={
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {"voice_name": "Charon"}
                }
            }
        }
    )
    print(f"finish_reason: {response.candidates[0].finish_reason}")
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'inline_data') and part.inline_data:
            with open('/tmp/tts_test2.wav', 'wb') as f:
                f.write(part.inline_data.data)
            print(f"Audio saved! {len(part.inline_data.data)} bytes")
        elif hasattr(part, 'text') and part.text:
            print(f"Text: {part.text[:100]}")
except Exception as e:
    print(f"Error: {e}")
