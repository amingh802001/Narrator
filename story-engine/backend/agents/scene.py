from .utils import parse_json, generate
from ..models import StoryConstitution, SceneBeat, GeneratedScene

PROMPT = """You are a literary writer. Write the actual prose for this story scene.

Story:
- Emotional signature: {emotional_signature}
- Theme: {theme}
- Protagonist: {protagonist_name}, core gap: {core_gap}

Previous: {previous_summary}

Current beat:
- Arc position: {arc_position}
- Title: {beat_title}
- What happens: {description}
- Character state: {character_state}
- World response: {world_response}

Return JSON:
{{
  "prose": "200 to 350 words of actual literary prose",
  "image_prompt": "detailed visual description for image generation",
  "narration_text": "prose cleaned for text to speech"
}}

Return ONLY valid JSON. No markdown fences, no explanation."""


async def generate_scene(
    constitution: StoryConstitution,
    beat: SceneBeat,
    previous_scenes: list[GeneratedScene],
    intervention: str = None,
) -> GeneratedScene:

    previous_summary = "This is the opening scene." if not previous_scenes else \
        " then ".join([f"{s.beat.title}: {s.beat.description[:60]}..."
                      for s in previous_scenes[-2:]])

    if intervention:
        prompt = f"""You are a literary writer redirecting a story.

Previous: {previous_summary}
User direction: {intervention}

Beat: {beat.arc_position} — {beat.description}
Character state: {beat.character_state}
Maintain: emotional signature: {constitution.emotional_signature}, theme: {constitution.theme}

Return JSON with prose, image_prompt, narration_text. ONLY valid JSON, no markdown."""
    else:
        prompt = PROMPT.format(
            emotional_signature=constitution.emotional_signature,
            theme=constitution.theme,
            protagonist_name=constitution.protagonist.name,
            core_gap=constitution.protagonist.core_gap,
            previous_summary=previous_summary,
            arc_position=beat.arc_position,
            beat_title=beat.title,
            description=beat.description,
            character_state=beat.character_state,
            world_response=beat.world_response,
        )

    text = await generate(prompt, temperature=0.9, max_tokens=1500)
    data = parse_json(text)

    return GeneratedScene(
        beat=beat,
        prose=data["prose"],
        image_prompt=data["image_prompt"],
        narration_text=data["narration_text"],
        image_url=None,
    )
