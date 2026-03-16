import base64
from .utils import MODEL
import google.generativeai as genai
import asyncio

STYLE_INSTRUCTIONS = {
    "EPIC":      "Speak with gravitas and weight. Slow your pace at moments of tension.",
    "WHIMSICAL": "Speak with warmth and lightness. Let wonder color your voice.",
    "TENSE":     "Speak with quiet urgency. Keep your voice controlled but coiled.",
    "LYRICAL":   "Speak with care and musicality. Honor the rhythm of sentences.",
    "NEUTRAL":   "Speak clearly and with presence.",
}

VOICE_MAP = {
    "EPIC":      "Charon",
    "WHIMSICAL": "Zephyr",
    "TENSE":     "Fenrir",
    "LYRICAL":   "Aoede",
    "NEUTRAL":   "Puck",
}

from ..models import VoiceStyle, GeneratedScene


def _generate_tts(text: str, voice_name: str, style_instruction: str) -> bytes:
    """Synchronous TTS call."""
    tts_model = genai.GenerativeModel("gemini-2.5-flash-preview-tts")
    prompt = f"{style_instruction}\n\nNarrate the following:\n\n{text}"

    response = tts_model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            response_mime_type="audio/wav",
            speech_config=genai.types.SpeechConfig(
                voice_config=genai.types.VoiceConfig(
                    prebuilt_voice_config=genai.types.PrebuiltVoiceConfig(
                        voice_name=voice_name
                    )
                )
            ),
        ),
    )

    # extract audio bytes from response parts
    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    return part.inline_data.data

    raise ValueError("No audio data in TTS response")


async def generate_narration(
    scene: GeneratedScene,
    voice_style: VoiceStyle,
) -> bytes:
    style_name = voice_style.name
    voice_name = VOICE_MAP.get(style_name, "Puck")
    style_instruction = STYLE_INSTRUCTIONS.get(style_name, "Speak clearly.")

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: _generate_tts(scene.narration_text, voice_name, style_instruction)
    )


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
