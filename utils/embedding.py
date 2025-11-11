import requests
import numpy as np
from utils.config import GEMINI_EMBED_URL

def get_gemini_embedding(text: str):
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]}
    }
    resp = requests.post(GEMINI_EMBED_URL, json=payload)
    if resp.status_code != 200:
        return None
    data = resp.json()
    return np.array(data["embedding"]["values"], dtype=np.float32)
