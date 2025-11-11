import requests
import datetime
from utils.helpers import video_to_base64, normalize_keys, parse_gemini_response
from utils.prompts import METADATA_PROMPT
from utils.config import GEMINI_CHAT_URL

def extract_video_metadata(video_path, video_name):
    video_b64 = video_to_base64(video_path)
    payload = {
        "contents": [
            {
                "parts": [
                    {"inlineData": {"mimeType": "video/mp4", "data": video_b64}},
                    {"text": METADATA_PROMPT}
                ]
            }
        ]
    }

    resp = requests.post(GEMINI_CHAT_URL, json=payload)
    if resp.status_code != 200:
        return {"title": video_name, "summary": f"Error extracting metadata: {resp.text}"}

    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    metadata = parse_gemini_response(text, video_name)
    metadata = normalize_keys(metadata)
    metadata["uploaded_by"] = "Huzaifa"
    metadata["created_at"] = datetime.datetime.utcnow().isoformat()
    return metadata
