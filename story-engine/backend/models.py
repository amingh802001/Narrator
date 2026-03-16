from pydantic import BaseModel, Field
from typing import Optional, Literal
from enum import Enum


class VoiceStyle(str, Enum):
    EPIC      = "Charon"    # deep, dramatic — epic/dark fantasy
    WHIMSICAL = "Zephyr"    # light, warm — fairy tale/comedy
    TENSE     = "Fenrir"    # taut, urgent — thriller/horror
    LYRICAL   = "Aoede"     # melodic, poetic — literary/romance
    NEUTRAL   = "Puck"      # clear, balanced — default


VOICE_SELECTION_PROMPT = """
You are selecting a narration voice for a story.
Based on the story's tone and genre, pick exactly one voice style:

- EPIC    → dark fantasy, mythology, war, tragedy, high stakes
- WHIMSICAL → fairy tale, comedy, adventure, children, magical realism
- TENSE   → thriller, horror, mystery, psychological, dystopia
- LYRICAL → literary fiction, romance, coming-of-age, poetry
- NEUTRAL → contemporary, sci-fi, general fiction, unclear tone

Respond with ONLY the single word: EPIC, WHIMSICAL, TENSE, LYRICAL, or NEUTRAL.
"""


class StoryMode(str, Enum):
    SEED       = "seed"        # user provides seed idea
    CHARACTER  = "character"   # user defines characters + world


class Character(BaseModel):
    name: str
    background: str
    core_gap: str               # the intolerable interior distance
    values: str
    surface_want: str
    deeper_need: str


class WorldModel(BaseModel):
    ethos: str                  # governing logic and character of world
    norms: str
    enforcement: str            # how the world pushes back
    world_gap: str              # the world's own internal tension


class StoryConstitution(BaseModel):
    core_identity: str          # what the story is fundamentally about
    emotional_signature: str    # how it should feel
    central_want_pain: str      # the engine
    theme: str                  # what it's really about beneath the surface
    world_contract: WorldModel
    protagonist: Character
    voice_style: VoiceStyle = VoiceStyle.NEUTRAL
    genre_hint: str = ""


class ArcCandidate(BaseModel):
    title: str
    logline: str                # one sentence story summary
    arc_shape: str              # how the arc unfolds
    core_conflict: str
    transformation: str         # who the protagonist becomes
    dramatic_appeal: str        # why this is compelling


class StoryPossibilities(BaseModel):
    candidates: list[ArcCandidate]  # always 3


class SceneBeat(BaseModel):
    beat_number: int
    title: str
    arc_position: Literal[
        "equilibrium", "disruption", "escalation",
        "false_peak", "crisis", "transformation"
    ]
    description: str            # what happens
    character_state: str        # internal state of protagonist
    world_response: str         # how the world pushes back


class StorySkeleton(BaseModel):
    chosen_arc: ArcCandidate
    beats: list[SceneBeat]      # 5-7 beats


class GeneratedScene(BaseModel):
    beat: SceneBeat
    prose: str                  # the actual written scene
    image_prompt: str           # prompt for image generation
    image_url: Optional[str] = None
    narration_text: str         # cleaned text for TTS


class StoryState(BaseModel):
    mode: StoryMode
    seed: Optional[str] = None
    constitution: Optional[StoryConstitution] = None
    possibilities: Optional[StoryPossibilities] = None
    chosen_arc_index: Optional[int] = None
    skeleton: Optional[StorySkeleton] = None
    scenes: list[GeneratedScene] = Field(default_factory=list)
    current_beat_index: int = 0
    user_interventions: list[str] = Field(default_factory=list)
    art_style: Optional[str] = None
    seed_image_base64: Optional[str] = None
    seed_image_mime: Optional[str] = None


# API request/response models
class InitRequest(BaseModel):
    mode: StoryMode
    seed: Optional[str] = None
    character: Optional[Character] = None
    world: Optional[WorldModel] = None
    image_base64: Optional[str] = None
    image_mime: Optional[str] = "image/jpeg"


class ChooseArcRequest(BaseModel):
    arc_index: int              # 0, 1, or 2
    user_note: Optional[str] = None


class InterventionRequest(BaseModel):
    instruction: str            # user's redirection instruction
    at_beat: int


class VoiceInputRequest(BaseModel):
    audio_base64: str
    mime_type: str = "audio/webm"
