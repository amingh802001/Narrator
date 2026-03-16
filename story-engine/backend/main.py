from dotenv import load_dotenv
load_dotenv()

import os
import base64
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import google.generativeai as genai

from .models import (
    StoryState, StoryMode, InitRequest,
    ChooseArcRequest, InterventionRequest, VoiceInputRequest,
)
from .agents import (
    build_constitution, generate_possibilities, generate_skeleton,
    generate_scene, generate_narration, transcribe_voice_input,
    generate_scene_image,
)

sessions: dict[str, StoryState] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)
    print(f"Gemini configured with API key: {api_key[:8]}...")
    yield

app = FastAPI(title="Story Engine", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

@app.get("/")
async def root():
    index = os.path.join(frontend_path, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"status": "Story Engine API running"}


@app.post("/story/{session_id}/set-style")
async def set_art_style(session_id: str, style: str):
    state = get_session(session_id)
    valid = ["cinematic","renaissance","anime","minimal","watercolor","noir","fantasy","cubism"]
    if style not in valid:
        raise HTTPException(status_code=400, detail=f"Style must be one of: {valid}")
    state.art_style = style
    return {"art_style": style}



@app.post("/story/{session_id}/regen-image/{beat_index}")
async def regen_image(session_id: str, beat_index: int):
    state = get_session(session_id)
    if beat_index >= len(state.scenes):
        raise HTTPException(status_code=404, detail="Scene not found")
    scene = state.scenes[beat_index]
    try:
        image_url = await generate_scene_image(
            scene=scene,
            voice_style=state.constitution.voice_style,
            constitution=state.constitution,
            previous_scenes=state.scenes[:beat_index],
            art_style=state.art_style,
            seed_image_base64=state.seed_image_base64,
            seed_image_mime=state.seed_image_mime,
        )
        if image_url:
            state.scenes[beat_index].image_url = image_url
        return {"image_url": image_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/session/new")
async def new_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = StoryState(mode=StoryMode.SEED)
    return {"session_id": session_id}

def get_session(session_id: str) -> StoryState:
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return sessions[session_id]

@app.post("/story/{session_id}/init")
async def init_story(session_id: str, req: InitRequest):
    state = get_session(session_id)
    state.mode = req.mode
    state.seed = req.seed
    try:
        constitution = await build_constitution(
            mode=req.mode, seed=req.seed,
            character=req.character, world=req.world,
            image_base64=req.image_base64,
            image_mime=req.image_mime,
        )
        state.constitution = constitution
        state.seed_image_base64 = req.image_base64
        state.seed_image_mime = req.image_mime
        possibilities = await generate_possibilities(constitution=constitution)
        state.possibilities = possibilities
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "constitution": constitution.model_dump(),
        "possibilities": possibilities.model_dump(),
        "voice_style": constitution.voice_style.name,
    }

@app.post("/story/{session_id}/choose-arc")
async def choose_arc(session_id: str, req: ChooseArcRequest):
    state = get_session(session_id)
    if not state.possibilities:
        raise HTTPException(status_code=400, detail="No possibilities generated yet")
    chosen = state.possibilities.candidates[req.arc_index]
    state.chosen_arc_index = req.arc_index
    try:
        skeleton = await generate_skeleton(
            constitution=state.constitution, chosen_arc=chosen,
        )
        state.skeleton = skeleton
        state.current_beat_index = 0
        state.scenes = []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"skeleton": skeleton.model_dump()}

@app.post("/story/{session_id}/next-scene")
async def next_scene(session_id: str, intervention: str = None):
    state = get_session(session_id)
    if not state.skeleton:
        raise HTTPException(status_code=400, detail="No skeleton generated yet")
    beat_index = state.current_beat_index
    if beat_index >= len(state.skeleton.beats):
        return {"done": True, "message": "Story complete"}
    beat = state.skeleton.beats[beat_index]
    try:
        scene = await generate_scene(
            constitution=state.constitution, beat=beat,
            previous_scenes=state.scenes, intervention=intervention,
        )
        image_url = await generate_scene_image(
            scene=scene,
            voice_style=state.constitution.voice_style,
            constitution=state.constitution,
            previous_scenes=state.scenes,
            art_style=state.art_style,
            seed_image_base64=state.seed_image_base64,
            seed_image_mime=state.seed_image_mime,
        )
        scene.image_url = image_url
        state.scenes.append(scene)
        state.current_beat_index += 1
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "scene": scene.model_dump(),
        "beat_index": beat_index,
        "total_beats": len(state.skeleton.beats),
        "is_final": beat_index == len(state.skeleton.beats) - 1,
    }

@app.post("/story/{session_id}/intervene")
async def intervene(session_id: str, req: InterventionRequest):
    state = get_session(session_id)
    state.user_interventions.append(req.instruction)
    state.current_beat_index = req.at_beat
    state.scenes = state.scenes[:req.at_beat]
    return await next_scene(session_id, intervention=req.instruction)

@app.post("/story/{session_id}/narrate/{beat_index}")
async def narrate_scene(session_id: str, beat_index: int):
    state = get_session(session_id)
    if beat_index >= len(state.scenes):
        raise HTTPException(status_code=404, detail="Scene not generated yet")
    scene = state.scenes[beat_index]
    try:
        audio_bytes = await generate_narration(
            scene=scene, voice_style=state.constitution.voice_style,
        )
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return {"audio_base64": audio_b64, "mime_type": "audio/mp3"}
    except NotImplementedError:
        raise HTTPException(status_code=503, detail="Narration not available in this version")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/transcribe")
async def transcribe_audio(req: VoiceInputRequest):
    try:
        text = await transcribe_voice_input(
            audio_base64=req.audio_base64, mime_type=req.mime_type,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"text": text}

@app.get("/story/{session_id}/state")
async def get_state(session_id: str):
    state = get_session(session_id)
    return state.model_dump()
