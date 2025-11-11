import streamlit as st
import tempfile
from utils.meta_extract import extract_video_metadata
from utils.embedding import get_gemini_embedding
from utils.database import save_embedding_pg, save_metadata_pg
from utils.qc import qc_score

st.set_page_config(page_title="Video Embeddings & QC")
st.title("Video Embeddings + QC")

if "session_metadata" not in st.session_state:
    st.session_state.session_metadata = {}

uploaded_videos = st.file_uploader(
    "Upload videos",
    type=["mp4", "mov", "avi"],
    accept_multiple_files=True
)

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    generate_btn = st.button("Generate Metadata + Score")
with col2:
    store_all_btn = st.button("Store All Embeddings")
with col3:
    clear_cache_btn = st.button("Clear Generated Metadata")

if clear_cache_btn:
    st.session_state.session_metadata = {}
    st.success("Cleared generated metadata cache.")    

if uploaded_videos and generate_btn:
    progress = st.progress(0)
    total = len(uploaded_videos)
    st.session_state.session_metadata = {}  
    for i, video_file in enumerate(uploaded_videos):
        with st.spinner(f"Analyzing {video_file.name} ({i + 1}/{total})..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                tmp.write(video_file.read())
                video_path = tmp.name
            try:
                metadata = extract_video_metadata(video_path, video_file.name)
                qc = qc_score(metadata)
                metadata.update(qc)
                st.session_state.session_metadata[video_file.name] = metadata
                st.subheader(video_file.name)
                # st.json(metadata)
                st.info(f"QC Score: {qc['qc_score']} | Decision: {qc['qc_decision']}")
                st.caption("Reasons: " + "; ".join(qc["qc_reasons"]))

            except Exception as e:
                st.error(f"❌ Error processing {video_file.name}: {e}")

            progress.progress((i + 1) / total)

    st.success("Metadata & QC Score generated. Use 'Store All' or per-video buttons below to save.")

if st.session_state.session_metadata:
    st.write("### Generated Metadata:")
    for name, meta in st.session_state.session_metadata.items():
        st.write(f"**{name}** — QC Score: {meta.get('qc_score')} | Decision: {meta.get('qc_decision')}")
        cols = st.columns([1, 1, 6])
        store_one = cols[0].button(f"Store {name}", key=f"store_{name}")
        inspect = cols[1].button(f"Inspect {name}", key=f"inspect_{name}")
        
        if inspect:
            st.json(meta)

        if store_one:
            try:
                emb = get_gemini_embedding(meta.get("summary", name))
                if emb is not None:
                    save_embedding_pg(name, emb, meta)
                    save_metadata_pg(name, meta)
                    st.success(f"Stored: {name}")
                else:
                    st.warning(f"⚠️ Skipped {name} due to embedding issue.")
            except Exception as e:
                st.error(f"❌ Error storing {name}: {e}")

if st.session_state.session_metadata and store_all_btn:
    progress = st.progress(0)
    items = list(st.session_state.session_metadata.items())
    total = len(items)

    for i, (video_name, metadata) in enumerate(items):
        with st.spinner(f"Storing {video_name} ({i + 1}/{total})..."):
            try:
                emb = get_gemini_embedding(metadata.get("summary", video_name))
                if emb is not None:
                    save_embedding_pg(video_name, emb, metadata)
                    save_metadata_pg(video_name, metadata)
                    st.success(f"✅ Stored: {video_name}")
                else:
                    st.warning(f"⚠️ Skipped {video_name} due to embedding issue.")
            except Exception as e:
                st.error(f"❌ Error storing {video_name}: {e}")
        progress.progress((i + 1) / total)

    st.success("All videos stored successfully!")
