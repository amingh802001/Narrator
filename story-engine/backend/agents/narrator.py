import base64
import asyncio
import google.generativeai as genai
from ..models import VoiceStyle, GeneratedScene


async def generate_narration(
    scene: GeneratedScene,
    voice_style: VoiceStyle,
) -> bytes:
    raise NotImplementedError("TTS handled by Web Speech API in frontend")


async def transcribe_voice_input(
    audio_base64: str,
    mime_type: str = "audio/webm",
) -> str:
    """Transcribe audio using Gemini's multimodal capability."""
    audio_bytes = base64.b64decode(audio_base64)

    # use gemini-2.5-flash for transcription — confirmed working
    model = genai.GenerativeModel("gemini-2.5-flash")

    loop = asyncio.get_running_loop()
    try:
        response = await loop.run_in_executor(
            None, lambda: model.generate_content([
                {"mime_type": mime_type, "data": audio_bytes},
                "Please transcribe exactly what is spoken in this audio recording. Return only the transcribed text, nothing else."
            ])
        )
        return response.text.strip()
    except Exception as e:
        # fallback — try with different mime type
        try:
            response = await loop.run_in_executor(
                None, lambda: model.generate_content([
                    {"mime_type": "audio/mp4", "data": audio_bytes},
                    "Transcribe exactly what is spoken. Return only the transcribed text."
                ])
            )
            return response.text.strip()
        except Exception as e2:
            raise ValueError(f"Transcription failed: {e2}")
