METADATA_PROMPT = """
You are analyzing a real estate or lifestyle video. Based on the full video content (visuals, audio, text), extract structured metadata in strict JSON format using the following schema.

Rules:
- Return only valid JSON.
- Ensure all Yes/No values are consistent ("Yes" or "No").
- For lists, return [] if nothing applies.
- Detect and flag ANY family-unfriendly or unsafe content (adult, explicit, violent, hateful, disturbing, substance use). These must always be captured.
- If the video references a UAE city or landmark (e.g., Dubai, Palm Jumeirah, Burj Khalifa, Abu Dhabi, Sharjah, Ras Al Khaimah, Marina, Jumeirah Beach, Downtown Dubai, Emirates Hills, Dubai Hills Estate), then mark `"uae_related": "Yes"`. Otherwise `"uae_related": "No"`.
- If UAE-related, also provide `"uae_sentiment"` as "Positive", "Neutral", or "Negative" based on portrayal.

{
  "title": "Modern Villa Tour in Dubai Hills Estate",
  "category": "Property",  // Options: Property, Lifestyle, Other
  "tags": ["Dubai", "Luxury", "Villa", "Modern Design"],
  "summary": "A luxury villa walkthrough in Dubai Hills. A female narrator describes the layout and design. The video features drone shots, interiors, bedrooms, pool, and garden.",
  "adult_content_presence": "No",
  "adult_content_type": [],  // ["Nudity", "Sexual themes", "Explicit language", "Kissing", "Suggestive clothing"]
  "violence_presence": "No",
  "violence_type": [],  // ["Fighting", "Weapons", "Blood", "Abuse"]
  "substance_use_presence": "No",
  "substance_use_type": [],  // ["Drugs", "Alcohol", "Smoking"]
  "hate_speech_presence": "No",
  "hate_speech_type": [],  // ["Racism", "Sexism", "Discrimination", "Religious hate"]
  "disturbing_content_presence": "No",
  "disturbing_content_type": [],  // ["Gore", "Graphic injury", "Self-harm", "Suicide"]
  "uae_related": "Yes",
  "uae_sentiment": "Positive",
  "is_real_estate_related": "Yes",
  "main_topic_category": "Real Estate",  // Real Estate, Lifestyle, Travel, Finance, Other
  "primary_intent": "Promote Property",  // Promote Property, Inspire Lifestyle, Educate, Drive Event, etc
  "secondary_intent": "Highlight Amenities",
  "emotional_appeal": "Aspirational",  // Aspirational, Comfort, Excitement, Prestige
  "urgency_cues": "None",  // Examples: "Limited units", "Pre-launch", "Only 2 left"
  "video_less_than_10_frames": "No",     // Yes / No -> MUST be "Yes" if complete video has fewer than 10 unique frames
  "event_driven": "No",
  "if_event_yes_time": "",  // Format: YYYY-MM-DD
  "speaker_presence": "Yes",
  "speaker_gender": "Female",
  "speaker_age_range": "30s",
  "speaker_accent": "British",
  "speaker_race": "White",
  "ai_visuals_presence": "No",
  "ai_generated_extent: "Partial" // None, Partial, Full
  "ai_voice_presence": "No",
  "primary_language_spoken": "English",
  "secondary_languages_spoken": [],
  "speakers": [
    {
      "gender": "Female",
      "age_range": "30s",
      "accent": "British",
      "race": "White",
      "ai_voice": false
    }
  ], // Optional: For videos with multiple speakers or voice types
  "voice_tone": "Professional",  // Warm, Friendly, Professional, Luxury, Excited
  "speech_speed": "Moderate",
  "clarity_of_speech": "Clear",
  "narration_style": "Guide",  // Guide, Sales Pitch, Storytelling, Informal Chat
  "background_music_presence": "Yes",
  "music_mood": "Calm",
  "music_type": "Ambient",
  "volume_balance": "Balanced",  // Balanced, Narration-dominant, Music-dominant
  "audio_sync": "In-sync",  // In-sync, Slightly Off, Off-sync
  "background_noise_level": "Low",  // None, Low, Medium, High
  "subtitles_present": "Yes",
  "subtitles_languages": ["English"],
  "text_overlays": ["Price: AED 15M", "5 Bed Villa", "Contact Agent"],
  "video_resolution": "4K",  // 720p, 1080p, 4K
  "frame_stability": "Stable",  // Stable, Slightly shaky, Shaky
  "lighting_quality": "Well-lit",  // Well-lit, Overexposed, Underexposed, Mixed
  "color_balance": "Natural",  // Natural, Warm, Cool, Oversaturated
  "mood_of_visuals": "Bright and Modern",
  "aesthetic_style": "Minimalist Luxury",  // Industrial, Classic, Contemporary, Modern, Boho
  "space_perception": "Spacious",  // Spacious, Cramped, Moderate
  "luxury_cues": ["High ceilings", "Private pool", "Smart home features"],
  "editing_quality": "Smooth",  // Smooth, Rough cuts, Amateur
  "transition_quality": "Cinematic",  // Cinematic, Simple cuts, Wipe, None
  "editing_style": "Slow-paced walkthrough",  // Fast-paced, Slow-paced, Match cut, Looping, Hyperlapse
  "shot_type": ["Drone", "Walkthrough", "POV", "Wide angle"],
  "camera_movements": ["Tracking", "Pan", "Tilt", "Static"],
  "indoor_vs_outdoor_focus": "Balanced",  // Indoor, Outdoor, Balanced
  "focus_balance": "Property-focused",  // Property-focused, Lifestyle-focused, Balanced
  "property_type": "Villa",
  "property_condition": "Brand New",
  "furnishing_level": "Fully Furnished",
  "rooms_shown": ["Living Room", "Kitchen", "Bedroom", "Bathroom", "Terrace"],
  "view_type": "Golf Course View",
  "indoor_amenities": ["Walk-in Closet", "Smart Home System", "Italian Kitchen"],
  "outdoor_amenities": ["Private Pool", "Garden", "Outdoor Seating"],
  "appliances_brands": ["Miele", "Siemens"],
  "category_of_brand": "High-end",
  "storytelling_style": "Linear Tour",  // Linear Tour, Mood-driven, Before/After, Testimonial
  "first_5s_focus": "Drone shot of the villa and location",
  "narrative_clarity": "Clear progression",  // Clear, Confusing, Abrupt cuts
  "call_to_action_presence": "Yes",
  "call_to_action_type": "Contact Agent",
  "logo_watermark": "Yes",
  "agent_branding_visible": "Yes",
  "developer_branding_visible": "No",
  "price_shown": "Yes",
  "price": {
    "value": 15000000,
    "currency": "AED"
  },
  "offer_mentioned": "No",
  "contact_info_shown": "Yes",
  "exclusivity_claim": "Exclusive Listing",
  "investment_pitch_signals": "Yes",
  "hook_style": "Visual hook",  // Visual hook, Verbal hook, No hook
  "video_duration": "2m 45s",  // Format: Xm Ys
  "aspect_ratio": "16:9",
  "activities_shown": ["Swimming", "Dining", "Working from home"],
  "lifestyle_emphasis": "Luxury Family Living",
  "user_engagement_elements": ["Text CTA", "Social handles"],
  "technical_glitches": "None"  // None, Minor, Severe
}
"""
