import streamlit as st
import requests

# -----------------------
# 🎨 Page Configuration
# -----------------------
st.set_page_config(page_title="📄 ScholarAssistant", layout="wide")
st.title("📄 ScholarAssistant: Talk with Your PDF")

# -----------------------
# 💾 Session State Setup
# -----------------------
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "pdf_summary" not in st.session_state:
    st.session_state.pdf_summary = ""
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None

# -----------------------
# 🧭 Sidebar: Upload Area
# -----------------------
st.sidebar.header("📤 Upload PDF")

uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type="pdf")

# If a new PDF is uploaded, reset the previous data
if uploaded_file:
    if uploaded_file.name != st.session_state.uploaded_filename:
        # New file detected → clear old data
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

# Optional: Button to clear chat manually
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.conversation_history = []
    st.sidebar.info("Chat history cleared.")

# -----------------------
# 📋 Display PDF Summary
# -----------------------
if st.session_state.pdf_summary:
    st.subheader("📝 PDF Summary")
    st.info(st.session_state.pdf_summary)

# -----------------------
# 💬 Chat Interface
# -----------------------
st.subheader("💬 Chat with Your PDF")

# Show previous conversation (chat-style)
for chat in st.session_state.conversation_history:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# Input for the next question
question = st.chat_input("Ask a question about the uploaded PDF...")

# -----------------------
# ⚡ Send Question to Backend
# -----------------------
if question:
    if not st.session_state.pdf_text:
        st.warning("Please upload a PDF first.")
    else:
        # Display user message immediately
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
