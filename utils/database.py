import numpy as np
import psycopg2
import datetime
import json
from utils.config import PG_CONN

def save_embedding_pg(video_name: str, embedding, metadata: dict):
    conn = psycopg2.connect(**PG_CONN)
    cur = conn.cursor()
    vector_str = "[" + ",".join(str(x) for x in embedding.tolist()) + "]"

    cur.execute("""
        INSERT INTO video_embeddings (video_name, embedding, metadata)
        VALUES (%s, %s::vector, %s)
    """, (video_name, vector_str, json.dumps(metadata)))

    conn.commit()
    cur.close()
    conn.close()

def get_existing_table_columns(cur, table_name="video_metadata"):
    cur.execute("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = %s
    """, (table_name,))
    return [r[0].lower() for r in cur.fetchall()]

def search_similar_videos(query_embedding: np.ndarray, top_k: int = 5):
    conn = psycopg2.connect(**PG_CONN)
    cur = conn.cursor()

    query_vector_str = "[" + ",".join(str(x) for x in query_embedding.tolist()) + "]"

    cur.execute(f"""
        SELECT video_name, metadata, embedding <-> %s::vector AS distance
        FROM video_embeddings
        ORDER BY embedding <-> %s::vector
        LIMIT %s;
    """, (query_vector_str, query_vector_str, top_k))

    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

def save_metadata_pg(video_name: str, metadata: dict):
    conn = psycopg2.connect(**PG_CONN)
    cur = conn.cursor()

    # Fields we expect to store
    expected_columns = [
        "video_name", "title", "category", "tags", "summary",
        "adult_content_presence", "adult_content_type", "is_real_estate_related",
        "main_topic_category", "speaker_presence", "location", "speaker_gender",
        "speaker_age_range", "speaker_accent", "speaker_race", "ai_voice_presence",
        "ai_visuals_presence", "primary_language_spoken", "secondary_languages_spoken",
        "voice_tone", "speech_speed", "clarity_of_speech", "narration_style",
        "background_music_presence", "music_mood", "music_type", "volume_balance",
        "property_type", "property_condition", "furnishing_level", "view_type",
        "indoor_vs_outdoor_focus", "rooms_shown", "outdoor_amenities", "appliances_brands",
        "category_of_brand", "indoor_amenities", "luxury_cues", "space_perception",
        "mood_of_visuals", "aesthetic_style", "shot_type", "storytelling_style",
        "focus_balance", "primary_intent", "secondary_intent", "emotional_appeal",
        "urgency_cues", "event_driven", "if_event_yes_time", "investment_pitch_signals",
        "call_to_action_presence", "call_to_action_type", "text_overlays", "logo_watermark",
        "price_shown", "price", "offer_mentioned", "contact_info_shown",
        "agent_branding_visible", "developer_branding_visible", "exclusivity_claim",
        "hook_strength", "first_5s_focus", "subtitles_present", "subtitles_languages",
        "activities_shown", "lifestyle_emphasis", "technical_glitches",
        "qc_score", "qc_decision", "qc_reasons",
        "uploaded_by", "created_at"
    ]

    # Fields that should be stored as boolean
    bool_fields = {
        "adult_content_presence", "is_real_estate_related", "speaker_presence",
        "ai_voice_presence", "ai_visuals_presence", "background_music_presence",
        "event_driven", "call_to_action_presence", "logo_watermark",
        "price_shown", "contact_info_shown", "agent_branding_visible",
        "developer_branding_visible", "subtitles_present"
    }

    # Fields that should be stored as arrays/JSON
    array_fields = {
        "tags", "adult_content_type", "secondary_languages_spoken",
        "outdoor_amenities", "subtitles_languages", "activities_shown",
        "rooms_shown", "indoor_amenities", "shot_type", "luxury_cues", "text_overlays",
        "appliances_brands"
    }

    try:
        db_cols = get_existing_table_columns(cur)
    except Exception as e:
        cur.close()
        conn.close()
        print(f"Error reading DB schema: {e}")
        return

    usable_columns = [c for c in expected_columns if c in db_cols]
    if not usable_columns:
        cur.close()
        conn.close()
        print("No matching columns in database.")
        return

    row = []
    for col in usable_columns:
        val = None
        if col == "video_name":
            val = video_name
        elif col == "uploaded_by":
            val = metadata.get("uploaded_by", "Huzaifa")
        elif col == "created_at":
            raw = metadata.get("created_at")
            try:
                val = datetime.datetime.fromisoformat(raw) if raw else datetime.datetime.utcnow()
            except:
                val = datetime.datetime.utcnow()
        else:
            val = metadata.get(col)

        # Convert booleans
        if col in bool_fields:
            if isinstance(val, str):
                val = val.strip().lower() == "yes"
            else:
                val = bool(val)

        # Convert array fields to JSON arrays
        if col in array_fields:
            if val is None:
                val = []
            elif isinstance(val, str):
                try:
                    parsed = json.loads(val)
                    val = parsed if isinstance(parsed, list) else [parsed]
                except:
                    val = [v.strip() for v in val.split(",") if v.strip()]
            elif not isinstance(val, list):
                val = [val]

        # Convert nested JSON fields (like price) to JSON string
        if col == "price" and isinstance(val, dict):
            val = json.dumps(val)

        # Convert qc_reasons list to string
        if col == "qc_reasons" and isinstance(val, list):
            val = "; ".join(val)

        row.append(val)

    placeholders = ", ".join(["%s"] * len(usable_columns))
    query = f"INSERT INTO video_metadata ({', '.join(usable_columns)}) VALUES ({placeholders})"

    try:
        cur.execute(query, row)
        conn.commit()
        print(f"✅ Metadata stored: {video_name}")
    except Exception as e:
        conn.rollback()
        print(f"❌ Error storing metadata: {e}")
    finally:
        cur.close()
        conn.close()
