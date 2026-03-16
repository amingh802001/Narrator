import asyncio
import google.generativeai as genai
from ..models import GeneratedScene, VoiceStyle

async def generate_scene_image(scene: GeneratedScene, voice_style: VoiceStyle) -> str | None:
    # Image generation via API key not supported — return None gracefully
    print(f"Image generation skipped (not available with API key): {scene.image_prompt[:50]}...")
    return None
