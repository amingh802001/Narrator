from .utils import parse_json, generate, MODEL
from ..models import (
    StoryConstitution, WorldModel, Character,
    VoiceStyle, VOICE_SELECTION_PROMPT, StoryMode
)

CONSTITUTION_FROM_SEED = """You are a story architect. Given a seed idea, extract the story's essential identity.

Seed idea: {seed}

Return a JSON object:
{{
  "core_identity": "what this story is fundamentally about in one sentence",
  "emotional_signature": "how this story should feel",
  "central_want_pain": "what the protagonist wants and what pain drives them",
  "theme": "what the story is really about beneath the surface",
  "genre_hint": "primary genre in 2-3 words",
  "world_contract": {{
    "ethos": "governing logic and character of this world",
    "norms": "what is normal and permissible here",
    "enforcement": "how this world pushes back against deviation",
    "world_gap": "the world's own internal tension"
  }},
  "protagonist": {{
    "name": "character name",
    "background": "brief background in 1-2 sentences",
    "core_gap": "the intolerable interior distance",
    "values": "what they protect",
    "surface_want": "what they consciously want",
    "deeper_need": "what they actually need"
  }}
}}

Return ONLY valid JSON. No markdown, no explanation."""

CONSTITUTION_FROM_CHARACTER = """You are a story architect. Synthesize a story constitution.

Character: {character}
World: {world}

Return a JSON object:
{{
  "core_identity": "what story naturally emerges here",
  "emotional_signature": "how this story should feel",
  "central_want_pain": "the engine from the character's core gap",
  "theme": "what this is really about beneath the surface",
  "genre_hint": "primary genre in 2-3 words",
  "world_contract": {{
    "ethos": "governing logic",
    "norms": "what is normal",
    "enforcement": "how the world pushes back",
    "world_gap": "internal tension"
  }},
  "protagonist": {{
    "name": "name",
    "background": "background",
    "core_gap": "the intolerable interior distance",
    "values": "what they protect",
    "surface_want": "conscious want",
    "deeper_need": "actual deeper need"
  }}
}}

Return ONLY valid JSON. No markdown, no explanation."""


async def build_constitution(
    mode: StoryMode,
    seed: str = None,
    character: Character = None,
    world: WorldModel = None,
) -> StoryConstitution:

    if mode == StoryMode.SEED:
        prompt = CONSTITUTION_FROM_SEED.format(seed=seed)
    else:
        prompt = CONSTITUTION_FROM_CHARACTER.format(
            character=character.model_dump_json(indent=2),
            world=world.model_dump_json(indent=2)
        )

    text = await generate(prompt, temperature=0.8, max_tokens=2000)
    data = parse_json(text)

    voice_prompt = VOICE_SELECTION_PROMPT + f"\n\nStory tone: {data['emotional_signature']}\nGenre: {data.get('genre_hint','')}"
    voice_text = await generate(voice_prompt, temperature=0.3, max_tokens=20)
    voice_str = voice_text.strip().upper().split()[0]
    try:
        voice_style = VoiceStyle[voice_str]
    except KeyError:
        voice_style = VoiceStyle.NEUTRAL

    return StoryConstitution(
        core_identity=data["core_identity"],
        emotional_signature=data["emotional_signature"],
        central_want_pain=data["central_want_pain"],
        theme=data["theme"],
        genre_hint=data.get("genre_hint", ""),
        world_contract=WorldModel(**data["world_contract"]),
        protagonist=Character(**data["protagonist"]),
        voice_style=voice_style,
    )
