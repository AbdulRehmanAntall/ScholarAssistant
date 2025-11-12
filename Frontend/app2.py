import streamlit as st
import requests

API_URL = "http://localhost:8000/citation_router/recommend"

st.set_page_config(page_title="Citation Recommender", layout="wide")

st.title("📚 Citation Recommender")

text = st.text_area("Paste your paragraph or abstract here:", height=200)

if st.button("Find Relevant Citations"):
    if not text.strip():
        st.warning("Please enter some text!")
    else:
        with st.spinner("Generating query and fetching papers..."):
            try:
                response = requests.post(API_URL, json={"text": text})
                response.raise_for_status()
                data = response.json()

                st.subheader("🔍 Generated Search Query")
                st.info(data["query"])

                st.subheader("📄 Top Papers")
                for paper in data["results"]:
                    with st.container():
                        st.markdown(f"**Title:** [{paper['title']}]({paper['link']})")
                        st.markdown(f"**Authors:** {', '.join(paper['authors'])}")
                        st.markdown(f"**Published:** {paper['published']}")
                        st.markdown(f"**Abstract:** {paper['summary'][:300]}{'...' if len(paper['summary'])>300 else ''}")
                        st.markdown("---")
            except Exception as e:
                st.error(f"Error: {e}")
