from .utils import parse_json, generate
from ..models import StoryConstitution, ArcCandidate, StoryPossibilities

PROMPT = """You are a story dramaturg. Propose exactly THREE dramatically distinct arc directions.

Story:
- Core identity: {core_identity}
- Engine: {central_want_pain}
- Theme: {theme}
- Protagonist core gap: {core_gap}
- Protagonist values: {values}
- World ethos: {world_ethos}
- World enforcement: {world_enforcement}
- World gap: {world_gap}

Return JSON:
{{
  "candidates": [
    {{"title": "title", "logline": "one sentence", "arc_shape": "how it unfolds", "core_conflict": "collision", "transformation": "who they become", "dramatic_appeal": "why compelling"}},
    {{"title": "title", "logline": "one sentence", "arc_shape": "how it unfolds", "core_conflict": "collision", "transformation": "who they become", "dramatic_appeal": "why compelling"}},
    {{"title": "title", "logline": "one sentence", "arc_shape": "how it unfolds", "core_conflict": "collision", "transformation": "who they become", "dramatic_appeal": "why compelling"}}
  ]
}}

Return ONLY valid JSON. No markdown, no explanation."""


async def generate_possibilities(constitution: StoryConstitution) -> StoryPossibilities:
    prompt = PROMPT.format(
        core_identity=constitution.core_identity,
        central_want_pain=constitution.central_want_pain,
        theme=constitution.theme,
        core_gap=constitution.protagonist.core_gap,
        values=constitution.protagonist.values,
        world_ethos=constitution.world_contract.ethos,
        world_enforcement=constitution.world_contract.enforcement,
        world_gap=constitution.world_contract.world_gap,
    )
    text = await generate(prompt, temperature=0.9, max_tokens=2500)
    data = parse_json(text)
    candidates = [ArcCandidate(**c) for c in data["candidates"][:3]]
    return StoryPossibilities(candidates=candidates)
