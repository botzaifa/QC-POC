import base64
import json
import re

def video_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def normalize_keys(metadata):
    new_meta = {}
    for k, v in metadata.items():
        new_key = k.lower().replace(" ", "_").replace("-", "_")
        new_meta[new_key] = v
    return new_meta

def parse_gemini_response(text: str, video_name: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return {"title": video_name, "summary": text.strip()[:500]}
