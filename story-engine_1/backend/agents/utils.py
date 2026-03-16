import json
import re
import asyncio
import google.generativeai as genai

MODEL = "gemini-2.5-flash-lite"


def parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        return json.loads(text)


def make_model():
    return genai.GenerativeModel(MODEL)


def _call_model(prompt: str, temperature: float, max_tokens: int) -> str:
    """Synchronous model call — runs in thread executor."""
    model = genai.GenerativeModel(MODEL)
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        ),
    )
    text = response.text
    print(f"[RAW] {repr(text[:500])}")
    return text


async def generate(prompt: str, temperature=0.8, max_tokens=2000) -> str:
    """Async wrapper — runs sync model call in thread pool."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: _call_model(prompt, temperature, max_tokens)
    )
