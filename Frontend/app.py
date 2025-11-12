import streamlit as st
import requests

# -----------------------
# 🎨 Page Config
# -----------------------
st.set_page_config(page_title="📄 ScholarAssistant", layout="wide")
st.title("📄 ScholarAssistant")

# -----------------------
# 🧭 Sidebar Navigation
# -----------------------
app_mode = st.sidebar.radio("Choose Feature:", ["Chat with PDF", "Citation Recommender"])

# -----------------------
# 1️⃣ Chat with PDF
# -----------------------
if app_mode == "Chat with PDF":
    # --- Session States ---
    for key in ["pdf_text", "pdf_summary", "conversation_history", "uploaded_filename"]:
        if key not in st.session_state:
            st.session_state[key] = "" if "text" in key or key == "uploaded_filename" else []

    # --- Upload PDF ---
    st.sidebar.header("📤 Upload PDF")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file:
        if uploaded_file.name != st.session_state.uploaded_filename:
            st.session_state.pdf_text = ""
            st.session_state.pdf_summary = ""
            st.session_state.conversation_history = []
            st.session_state.uploaded_filename = uploaded_file.name

            files = {"files": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            with st.spinner("📚 Extracting and summarizing your PDF..."):
                response = requests.post("http://127.0.0.1:8000/pdf/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                st.session_state.pdf_text = data["pdf_texts"][0]
                st.session_state.pdf_summary = data["summaries"][0]
                st.sidebar.success(f"✅ '{uploaded_file.name}' uploaded successfully!")
            else:
                st.sidebar.error("❌ Error uploading the PDF.")

    if st.sidebar.button("🗑️ Clear Chat"):
        st.session_state.conversation_history = []
        st.sidebar.info("Chat history cleared.")

    # --- PDF Summary ---
    if st.session_state.pdf_summary:
        st.subheader("📝 PDF Summary")
        st.info(st.session_state.pdf_summary)

    # --- Chat Interface ---
    st.subheader("💬 Chat with Your PDF")
    for chat in st.session_state.conversation_history:
        with st.chat_message(chat["role"]):
            st.markdown(chat["content"])

    question = st.chat_input("Ask a question about the uploaded PDF...")
    if question:
        if not st.session_state.pdf_text:
            st.warning("Please upload a PDF first.")
        else:
            st.chat_message("user").markdown(question)
            st.session_state.conversation_history.append({"role": "user", "content": question})

            payload = {
                "pdf_texts": [st.session_state.pdf_text],
                "question": question,
                "conversation_history": "\n".join(
                    [f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.conversation_history]
                ),
            }
            with st.spinner("🤔 Thinking..."):
                response = requests.post("http://127.0.0.1:8000/pdf/question", json=payload)
            if response.status_code == 200:
                answer = response.json()["answer"]
                with st.chat_message("assistant"):
                    st.markdown(answer)
                st.session_state.conversation_history.append({"role": "assistant", "content": answer})
            else:
                st.error(f"❌ Error generating answer: {response.text}")

# -----------------------
# 2️⃣ Citation Recommender
# -----------------------
elif app_mode == "Citation Recommender":
    # --- Session States ---
    for key in ["citation_results", "search_query", "text_input"]:
        if key not in st.session_state:
            st.session_state[key] = [] if key == "citation_results" else ""

    st.subheader("📚 Citation Recommender")

    # --- Input Form ---
    with st.form("citation_form", clear_on_submit=False):
        st.session_state.text_input = st.text_area(
            "Paste your paragraph or abstract here:", 
            height=200, 
            value=st.session_state.text_input
        )
        submitted = st.form_submit_button("🔍 Find Relevant Citations")

    # --- API Call ---
    if submitted:
        if not st.session_state.text_input.strip():
            st.warning("Please enter some text!")
        else:
            with st.spinner("Generating query and fetching papers..."):
                try:
                    API_URL = "http://localhost:8000/citation_router/recommend"
                    response = requests.post(API_URL, json={"text": st.session_state.text_input})
                    response.raise_for_status()
                    data = response.json()

                    st.session_state.search_query = data["query"]
                    st.session_state.citation_results = data["results"]

                except Exception as e:
                    st.error(f"❌ Error: {e}")

        # --- Display Results ---
        # --- Display Results ---
    if st.session_state.citation_results:
        st.markdown("### 🔍 Generated Search Query")
        st.info(st.session_state.search_query)

        st.markdown("### 📄 Top Papers")
        for paper in st.session_state.citation_results:
            with st.container():
                st.markdown(
                    f"""
                    <div style="border:1px solid #e0e0e0; padding:15px; border-radius:10px; margin-bottom:10px; background-color:#f9f9f9">
                        <h4 style="margin:0; color:#2B7A78;">{paper['title']}</h4>
                        <p style="margin:0; font-size:14px; color:#555;"><strong>Authors:</strong> {', '.join(paper['authors'])}</p>
                        <p style="margin:0; font-size:14px; color:#555;"><strong>Published:</strong> {paper['published']}</p>
                        <p style="margin:0; font-size:14px; color:#555;"><strong>Semantic Score:</strong> {paper['score']:.4f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # Collapsible Abstract using Streamlit expander
                with st.expander("📖 Abstract"):
                    st.write(paper['summary'])

                # ArXiv link
                st.markdown(f"[🔗 View on ArXiv]({paper['link']})")

                # BibTeX download
                bibtex = f"""@article{{,
    title={{ {paper['title']} }},
    author={{ {', '.join(paper['authors'])} }},
    journal={{ arXiv }},
    year={{ {paper['published'][:4]} }},
    url={{ {paper['link']} }}
    }}"""
                st.download_button(
                    label="📥 Download BibTeX",
                    data=bibtex,
                    file_name=f"{paper['title']}.bib",
                    mime="text/plain",
                    key=f"bib_{paper['title']}"
                )
