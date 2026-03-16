import base64
import asyncio
import google.generativeai as genai
from ..models import VoiceStyle, GeneratedScene


async def generate_narration(
    scene: GeneratedScene,
    voice_style: VoiceStyle,
) -> bytes:
    raise NotImplementedError("TTS coming in next version")


async def transcribe_voice_input(
    audio_base64: str,
    mime_type: str = "audio/webm",
) -> str:
    audio_bytes = base64.b64decode(audio_base64)
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    loop = asyncio.get_running_loop()
    response = await loop.run_in_executor(
        None, lambda: model.generate_content([
            {"mime_type": mime_type, "data": audio_bytes},
            "Transcribe this audio exactly. Return only the transcription."
        ])
    )
    return response.text.strip()
