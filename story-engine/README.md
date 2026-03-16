# Story Engine

**A multi-agent AI story construction system built for the Gemini Live Agent Challenge.**

Story Engine is a creative storytelling agent that moves beyond text-in/text-out. 
It uses a pipeline of specialized Gemini agents to build narratively coherent, 
emotionally resonant stories with inline generated illustrations, contextually 
selected narration voice, and real-time user intervention at any story beat.

---

## Architecture

```
User Input (text or voice)
        ↓
Story Constitution Agent  — crystallizes the story's north star
        ↓
Story Possibility Agent   — generates 3 dramatically distinct arc directions
        ↓
User chooses arc
        ↓
Skeleton Agent            — generates 6 dramatic beats (full arc)
        ↓
For each beat:
  Scene Agent             — writes literary prose for the scene
  Image Agent (Imagen 3)  — generates scene illustration
  Narrator Agent (TTS)    — generates contextually voiced narration
        ↓
User can intervene at any beat → redirects generation from that point
```

### Agent Roles
- **Constitution agent** — extracts core identity, theme, protagonist psychology, world contract, and selects narration voice based on emotional signature
- **Possibility agent** — finds dramatic collision points between character gaps and world enforcement; proposes 3 semantically distinct arc directions
- **Skeleton agent** — generates 6 causally connected beats following the dramatic arc (equilibrium → disruption → escalation → false peak → crisis → transformation)
- **Scene agent** — writes literary prose using emotional signature as stylistic guide; produces image prompt and narration text
- **Image agent** — generates scene illustration via Imagen 3 with style modifiers matched to story tone
- **Narrator agent** — generates TTS audio using voice preset selected by the constitution agent

### Technologies
- **Gemini 2.0 Flash** — all text generation agents
- **Gemini 2.5 Flash TTS** — narration generation
- **Imagen 3** — scene image generation
- **Google GenAI SDK** — all Gemini API calls
- **Google Cloud Run** — backend hosting
- **FastAPI** — backend API framework
- **Voice input** — browser MediaRecorder API + Gemini transcription

---

## Local Development

### Prerequisites
- Python 3.11+
- A Gemini API key
- Google Cloud CLI (for deployment only)

### Setup

```bash
# Clone the repo
git clone <your-repo-url>
cd story-engine

# Install dependencies
pip install -r backend/requirements.txt

# Set your API key
export GEMINI_API_KEY=your_key_here

# Run locally
uvicorn backend.main:app --reload --port 8080
```

Open `http://localhost:8080` in your browser.

---

## Cloud Run Deployment

### Quick deploy (recommended)

```bash
chmod +x deploy.sh
./deploy.sh YOUR_GCP_PROJECT_ID YOUR_GEMINI_API_KEY
```

### Manual deploy

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  containerregistry.googleapis.com aiplatform.googleapis.com

# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/story-engine

# Deploy
gcloud run deploy story-engine \
  --image gcr.io/YOUR_PROJECT_ID/story-engine \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GEMINI_API_KEY=YOUR_KEY" \
  --memory 512Mi
```

---

## Project Structure

```
story-engine/
├── backend/
│   ├── main.py              # FastAPI app + API routes
│   ├── models.py            # Pydantic data models
│   ├── agents/
│   │   ├── constitution.py  # Story constitution agent
│   │   ├── possibility.py   # Story possibility agent
│   │   ├── skeleton.py      # Arc skeleton agent
│   │   ├── scene.py         # Scene generation agent
│   │   ├── narrator.py      # TTS narration agent
│   │   └── image.py         # Image generation agent
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Single page app
│   ├── app.js               # Voice + text interaction logic
│   └── style.css            # UI styles
├── Dockerfile               # Container definition
├── cloudbuild.yaml          # GCP Cloud Build config
├── deploy.sh                # One-command deployment script
└── README.md
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/session/new` | Create new story session |
| POST | `/story/{id}/init` | Initialize with seed or character/world |
| POST | `/story/{id}/choose-arc` | Select arc direction (0-2) |
| POST | `/story/{id}/next-scene` | Generate next scene |
| POST | `/story/{id}/intervene` | Redirect story at a beat |
| POST | `/story/{id}/narrate/{beat}` | Generate TTS for a scene |
| POST | `/voice/transcribe` | Transcribe voice input |
| GET  | `/story/{id}/state` | Get full session state |
| GET  | `/health` | Health check |

---

## How to Demo

1. Open the app and enter a seed idea or define a character/world
2. Review the generated Story Constitution — note the AI-selected narration voice
3. Choose one of 3 dramatically distinct arc directions
4. Step through the story beat by beat
5. Click 🔊 Narrate to hear a scene read aloud in the contextually chosen voice
6. Use "Redirect the story" to intervene and see the agent adapt
7. Try voice input using the 🎙 button

---

*Built for the Gemini Live Agent Challenge — March 2026*
