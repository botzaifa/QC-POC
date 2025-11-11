import datetime

def qc_score(metadata: dict):
    # --- Early model/system error ---
    if "error" in metadata:
        return {
            "qc_score": 'N/A',
            "qc_decision": "ERROR",
            "qc_reasons": [f"Model error: {metadata['error'].get('message', 'Unknown error')}"]
        }
    score = 0
    reasons = []

    def add(points, reason):
        nonlocal score
        score += points
        reasons.append(f"{reason} ({'+' if points>0 else ''}{points})")

    def yn(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.strip().lower() in ["yes", "true", "y", "1"]
        return False

    def listify(x):
        if x is None:
            return []
        if isinstance(x, list):
            return x
        if isinstance(x, str):
            return [x]
        return list(x)

    # --- Reject conditions: <10 frames or <5 seconds ---
    vid_lt10 = (metadata.get("video_less_than_10_frames") or "").strip().lower()
    if vid_lt10 == "yes":
        return {
            "qc_score": 'N/A',
            "qc_decision": "REJECT",
            "qc_reasons": ["Rejected: video contains fewer than 10 unique frames"]
        }

    try:
        duration = float(metadata.get("video_duration", 0))
        if duration < 5:
            return {
                "qc_score": 'N/A',
                "qc_decision": "REJECT",
                "qc_reasons": [f"Rejected: video too short ({duration:.2f}s < 5s)"]
            }
    except:
        pass

    try:
        adult_presence = str(metadata.get("adult_content_presence", "")).strip().lower()
        adult_type = [t.strip().lower() for t in listify(metadata.get("adult_content_type"))]

        violence_presence = str(metadata.get("violence_presence", "")).strip().lower()
        violence_type = [t.strip().lower() for t in listify(metadata.get("violence_type"))]

        substance_presence = str(metadata.get("substance_use_presence", "")).strip().lower()
        substance_type = [t.strip().lower() for t in listify(metadata.get("substance_use_type"))]

        hate_presence = str(metadata.get("hate_speech_presence", "")).strip().lower()
        hate_type = [t.strip().lower() for t in listify(metadata.get("hate_speech_type"))]

        disturbing_presence = str(metadata.get("disturbing_content_presence", "")).strip().lower()
        disturbing_type = [t.strip().lower() for t in listify(metadata.get("disturbing_content_type"))]

        unsafe_flags = []
        if adult_presence == "yes": unsafe_flags.extend(adult_type)
        if violence_presence == "yes": unsafe_flags.extend(violence_type)
        if substance_presence == "yes": unsafe_flags.extend(substance_type)
        if hate_presence == "yes": unsafe_flags.extend(hate_type)
        if disturbing_presence == "yes": unsafe_flags.extend(disturbing_type)

        if unsafe_flags:
            return {
                "qc_score": 'N/A',
                "qc_decision": "REJECT",
                "qc_reasons": [f"Unsafe/NSFW content detected: {', '.join([f for f in unsafe_flags if f])}"]
            }
        else:
            add(+20, "No unsafe content")

    except:
        pass

    try:
        ai_extent = (metadata.get("ai_generated_extent") or "").strip().lower()
        if ai_extent == "full":
            add(-10, "Fully AI-generated video")
            return {
                "qc_score": 'N/A',
                "qc_decision": "MANUAL_REVIEW",
                "qc_reasons": ["The Video is completely AI Generated"]
            }
        elif ai_extent == "partial":
            add(0, "Partially AI-generated")
        else:
            add(0, "Not AI generation")
    except:
        pass

    # --- Real Estate / Lifestyle Relevance ---
    if yn(metadata.get("is_real_estate_related")) or \
       (metadata.get("main_topic_category") or "").strip().lower() in ["real estate", "property"]:
        add(+20, "Real estate related")
    else:
        cat = (metadata.get("main_topic_category") or "").strip().lower()
        if cat == "lifestyle":
            lifestyle = (metadata.get("lifestyle_emphasis") or "").strip().lower()
            if any(x in lifestyle for x in ["uae", "dubai", "abu dhabi", "sharjah"]):
                add(+10, "UAE lifestyle content")

    # --- UAE Relevance ---
    uae_related = (metadata.get("uae_related") or "").strip().lower()
    uae_sentiment = (metadata.get("uae_sentiment") or "").strip().lower()

    if uae_related == "yes":
        if uae_sentiment == "negative":
            add(-100, "Negative portrayal of UAE")
        else:
            add(+20, f"UAE related ({uae_sentiment.capitalize()})")
    else:
        add(0, "Not UAE-related → Manual review required")

    # --- Event / Time Validity ---
    if yn(metadata.get("event_driven")):
        event_time = metadata.get("if_event_yes_time")
        if event_time:
            try:
                event_dt = datetime.datetime.fromisoformat(event_time)
                if event_dt < datetime.datetime.utcnow():
                    add(-100, "Past event")
                else:
                    add(+15, "Upcoming/live event")
            except:
                add(0, "Invalid event time format")
        else:
            add(-10, "Event flagged but time missing")

    # --- Speech & Narration ---
    clarity = (metadata.get("clarity_of_speech") or "").strip().lower()
    if clarity == "clear":
        add(+10, "Clear & moderate narration")
    else:
        add(-10, "Unclear/missing narration")

    # --- Volume Balance ---
    vb = (metadata.get("volume_balance") or "").strip().lower()
    if vb in ["narration-dominant", "balanced"]:
        add(+10, "Good volume balance")
    elif vb == "music-dominant":
        add(-5, "Music too loud")

    # --- Visual Quality ---
    visuals = (metadata.get("mood_of_visuals") or "").strip().lower()
    if any(x in visuals for x in ["clear", "bright", "modern", "luxury", "well-lit"]):
        add(+10, "Good visuals")
    else:
        add(-10, "Poor/unclear visuals")

    # --- Subtitles ---
    if yn(metadata.get("subtitles_present")):
        add(+5, "Subtitles present")

    # --- Property Details ---
    rooms = metadata.get("rooms_shown")
    if rooms and (isinstance(rooms, list) and len(rooms) > 0 or isinstance(rooms, str) and rooms.strip()):
        add(+20, "Property details shown")

    # --- Technical QC ---
    glitches = (metadata.get("technical_glitches") or "").strip().lower()
    if glitches in ["none", "no", "clean"]:
        add(+20, "Clean technical quality")
    elif glitches in ["minor"]:
        add(-10, "Minor technical glitches")
    elif glitches in ["severe", "yes"]:
        add(-20, "Severe technical glitches")

    # --- Final decision ---
    if score >= 70:
        decision = "ACCEPT"
    elif score <= 0:
        decision = "REJECT"
    else:
        decision = "MANUAL_REVIEW"

    # Force manual review if UAE is not mentioned at all
    if uae_related != "yes" and decision == "ACCEPT":
        decision = "MANUAL_REVIEW"

    return {
        "qc_score": score,
        "qc_decision": decision,
        "qc_reasons": reasons
    }
