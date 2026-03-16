import asyncio
import base64
import google.generativeai as genai
from .utils import generate, MODEL
from ..models import GeneratedScene, VoiceStyle, StoryConstitution

# Art style presets — user can choose one
ART_STYLES = {
    "cinematic":    "cinematic photography, dramatic lighting, film still, 35mm",
    "renaissance":  "Renaissance oil painting, chiaroscuro, classical composition, Rembrandt lighting",
    "anime":        "anime illustration, Studio Ghibli style, detailed background, painterly",
    "minimal":      "minimalist illustration, clean lines, limited color palette, geometric",
    "watercolor":   "soft watercolor painting, loose brushwork, delicate washes, artistic",
    "noir":         "film noir, high contrast black and white, dramatic shadows, 1940s",
    "fantasy":      "epic fantasy digital art, detailed, atmospheric, painterly",
    "cubism":       "cubist painting, fragmented forms, multiple perspectives, Picasso inspired",
}

# Default style per voice/tone
TONE_STYLE_MAP = {
    "EPIC":      "cinematic",
    "WHIMSICAL": "watercolor",
    "TENSE":     "noir",
    "LYRICAL":   "renaissance",
    "NEUTRAL":   "cinematic",
}


async def generate_image_prompt(
    scene: GeneratedScene,
    constitution: StoryConstitution,
    previous_scenes: list[GeneratedScene],
) -> str:
    """
    Dedicated image prompt agent — generates a short, consistent,
    highly specific visual prompt for the scene.
    """
    prev_descriptions = ""
    if previous_scenes:
        prev_descriptions = "\n".join([
            f"- Scene {i+1}: {s.image_prompt[:80]}"
            for i, s in enumerate(previous_scenes[-2:])
        ])

    prompt = f"""You are a visual director creating image prompts for a story.

Story visual identity:
- Emotional signature: {constitution.emotional_signature}
- Theme: {constitution.theme}
- Protagonist: {constitution.protagonist.name}

Previous scene visuals (for consistency):
{prev_descriptions if prev_descriptions else "This is the first scene."}

Current scene:
- Arc position: {scene.beat.arc_position}
- What happens: {scene.beat.description}
- Character state: {scene.beat.character_state}

Write a single image generation prompt (max 60 words) that:
1. Describes the KEY visual moment of this scene specifically
2. Maintains visual consistency with previous scenes (same character appearance, world aesthetic)
3. Includes lighting and mood matching the arc position
4. Is concrete and specific — no abstract concepts

Return ONLY the prompt text, nothing else."""

    return await generate(prompt, temperature=0.7, max_tokens=150)


async def generate_scene_image(
    scene: GeneratedScene,
    voice_style: VoiceStyle,
    constitution: StoryConstitution = None,
    previous_scenes: list[GeneratedScene] = None,
    art_style: str = None,
    seed_image_base64: str = None,
    seed_image_mime: str = None,
) -> str | None:
    """Generate scene image using gemini-2.5-flash-image."""

    # determine art style
    if not art_style:
        style_name = TONE_STYLE_MAP.get(voice_style.name, "cinematic")
    else:
        style_name = art_style
    style_modifier = ART_STYLES.get(style_name, ART_STYLES["cinematic"])

    # get consistent image prompt
    if constitution and previous_scenes is not None:
        try:
            image_prompt = await generate_image_prompt(scene, constitution, previous_scenes)
            image_prompt = image_prompt.strip()
        except Exception:
            image_prompt = scene.image_prompt
    else:
        image_prompt = scene.image_prompt

    full_prompt = f"{image_prompt}. Style: {style_modifier}. No text or watermarks."

    loop = asyncio.get_running_loop()
    try:
        image_data = await loop.run_in_executor(
            None, lambda: _generate_image(full_prompt, seed_image_base64, seed_image_mime)
        )
        return image_data
    except Exception as e:
        print(f"Image generation failed: {e}")
        return None


def _generate_image(prompt: str, seed_image_base64: str = None, seed_image_mime: str = None) -> str | None:
    """Synchronous image generation using gemini-2.5-flash-image."""
    import base64
    model = genai.GenerativeModel("gemini-2.5-flash-image")

    if seed_image_base64:
        # use seed image for visual reference
        image_bytes = base64.b64decode(seed_image_base64)
        contents = [
            {"mime_type": seed_image_mime or "image/jpeg", "data": image_bytes},
            f"Using the visual style and elements from this reference image, generate a new scene image: {prompt}"
        ]
        response = model.generate_content(contents)
    else:
        response = model.generate_content(prompt)

    # extract image from response parts
    for candidate in response.candidates:
        if candidate.content and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    mime = part.inline_data.mime_type
                    data = part.inline_data.data
                    b64 = base64.b64encode(data).decode("utf-8")
                    return f"data:{mime};base64,{b64}"
    return None
