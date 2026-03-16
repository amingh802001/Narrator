from .utils import parse_json, generate
from ..models import StoryConstitution, ArcCandidate, SceneBeat, StorySkeleton

PROMPT = """Generate exactly 6 dramatic scene beats.

Arc positions: equilibrium, disruption, escalation, false_peak, crisis, transformation

Story:
- Core identity: {core_identity}
- Engine: {central_want_pain}
- Protagonist: {protagonist_name}, core gap: {core_gap}, values: {values}
- World: {world_ethos}, enforcement: {world_enforcement}

Chosen Arc:
- Title: {arc_title}
- Logline: {arc_logline}
- Conflict: {arc_conflict}
- Transformation: {arc_transformation}

Return JSON:
{{
  "beats": [
    {{"beat_number": 1, "title": "title", "arc_position": "equilibrium", "description": "2-3 sentences", "character_state": "internal state", "world_response": "world response"}},
    {{"beat_number": 2, "title": "title", "arc_position": "disruption", "description": "2-3 sentences", "character_state": "internal state", "world_response": "world response"}},
    {{"beat_number": 3, "title": "title", "arc_position": "escalation", "description": "2-3 sentences", "character_state": "internal state", "world_response": "world response"}},
    {{"beat_number": 4, "title": "title", "arc_position": "false_peak", "description": "2-3 sentences", "character_state": "internal state", "world_response": "world response"}},
    {{"beat_number": 5, "title": "title", "arc_position": "crisis", "description": "2-3 sentences", "character_state": "internal state", "world_response": "world response"}},
    {{"beat_number": 6, "title": "title", "arc_position": "transformation", "description": "2-3 sentences", "character_state": "internal state", "world_response": "world response"}}
  ]
}}

Return ONLY valid JSON. No markdown, no explanation."""


async def generate_skeleton(
    constitution: StoryConstitution,
    chosen_arc: ArcCandidate,
) -> StorySkeleton:
    prompt = PROMPT.format(
        core_identity=constitution.core_identity,
        central_want_pain=constitution.central_want_pain,
        protagonist_name=constitution.protagonist.name,
        core_gap=constitution.protagonist.core_gap,
        values=constitution.protagonist.values,
        world_ethos=constitution.world_contract.ethos,
        world_enforcement=constitution.world_contract.enforcement,
        arc_title=chosen_arc.title,
        arc_logline=chosen_arc.logline,
        arc_conflict=chosen_arc.core_conflict,
        arc_transformation=chosen_arc.transformation,
    )
    text = await generate(prompt, temperature=0.85, max_tokens=3000)
    data = parse_json(text)
    beats = [SceneBeat(**b) for b in data["beats"]]
    return StorySkeleton(chosen_arc=chosen_arc, beats=beats)
