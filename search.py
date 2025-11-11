import streamlit as st
from utils.embedding import get_gemini_embedding
from utils.database import search_similar_videos

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="Video Search", layout="centered")

st.title("Video Search from Embeddings")

st.markdown(
    """
    Enter a natural language query to find videos semantically similar in content.  
    Example: *Give me videos that have female in it*.
    """,
    unsafe_allow_html=True,
)

# Center container
with st.container():
    st.markdown("<div style='max-width:600px; margin: auto;'>", unsafe_allow_html=True)

    query = st.text_input("Enter your search query here")

    top_k = st.text_input("Enter number of results to show", value="3")

    # top_k = st.selectbox(
    #     "Number of results to show",
    #     options=[1, 3, 5, 7, 10],
    #     index=2,
    #     help="Select how many top results to display"
    # )

    search_button = st.button("Search")

    st.markdown("</div>", unsafe_allow_html=True)

if search_button:
    if not query.strip():
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Embedding query and searching..."):
            embedding = get_gemini_embedding(query)
            if embedding is not None:
                results = search_similar_videos(embedding, top_k=top_k)
                if results:
                    st.success(f"Found {len(results)} matching videos:")
                    for idx, (video_name, metadata, score) in enumerate(results, 1):
                        with st.expander(f"{idx}. {video_name} — Similarity Score: {score:.4f}"):
                            st.json(metadata)
                else:
                    st.warning("No matching videos found.")
            else:
                st.error("Failed to generate embedding for the query.")
