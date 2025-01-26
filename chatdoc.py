import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.vectorstores import Pinecone
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAI
from pinecone import Pinecone

# Initialize session state variables
if "current_query" not in st.session_state:
    st.session_state["current_query"] = ""

if "current_answer" not in st.session_state:
    st.session_state["current_answer"] = ""

if "query_history" not in st.session_state:
    st.session_state["query_history"] = []


# Load environment variables from .env file
load_dotenv()

# Constants from environment variables
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")

# Streamlit Page Setup
def setup_streamlit_page():
    st.title("📄 Chat with Your Documents")
    st.markdown("Welcome! Upload a document, and ask any questions about its content.")
    st.sidebar.header("📂 Upload and Manage Documents")
    st.sidebar.info("Supported Format: PDF")

# Initialize Pinecone Client
def initialize_pinecone():
    return Pinecone(api_key=PINECONE_API_KEY).Index(INDEX_NAME)

# Process and Store PDF in Pinecone (with caching)
def process_and_store_pdfs(uploaded_file, index):
    file_id = uploaded_file.name
    
    if file_id in st.session_state:
        st.sidebar.info("✅ Document already processed. Using cached data.")
        return st.session_state[file_id]["chunk_count"]
    
    reader = PdfReader(uploaded_file)
    text_data = "\n".join([reader.pages[i].extract_text() for i in range(len(reader.pages))])
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_text(text_data)
    
    embeddings = HuggingFaceEmbeddings()
    chunk_embeddings = embeddings.embed_documents(chunks)

    st.sidebar.info("📤 Indexing document into Pinecone...")
    progress_bar = st.sidebar.progress(0)
    vectors = [
        {
            "id": f"{file_id}-chunk-{i}",
            "values": embedding,
            "metadata": {"text": chunk}
        }
        for i, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings))
    ]
    progress_bar.progress(1.0)
    index.upsert(vectors)

    st.session_state[file_id] = {
        "chunk_count": len(chunks),
        "chunks": chunks,
        "vectors": vectors
    }

    st.sidebar.success("🎉 Document indexed successfully!")
    return len(chunks)

# Handle File Upload
def handle_file_upload(index):
    uploaded_file = st.sidebar.file_uploader(
        "📂 Drag and drop or click to upload a PDF file",
        type=["pdf"],
        label_visibility="visible"
    )
    if uploaded_file:
        st.sidebar.info(f"**Uploaded File:** {uploaded_file.name}")
        st.sidebar.success(f"File uploaded successfully! File size: {uploaded_file.size / 1024:.2f} KB")
        
        if "chunk_count" not in st.session_state:
            try:
                st.session_state["chunk_count"] = process_and_store_pdfs(uploaded_file, index)
            except Exception as e:
                st.sidebar.error(f"An error occurred while processing the document: {e}")
                st.stop()

        return uploaded_file
    return None

# Query Pinecone
def query_pinecone(index, query, top_k=5):
    embeddings = HuggingFaceEmbeddings()
    query_embedding = embeddings.embed_query(query)
    return index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

# Generate Answer using Google Gemini
def generate_answer(context, query):
    model = GoogleGenerativeAI(
        model="gemini-pro",
        temperature=0.5,
        max_output_tokens=2048
    )
    prompts = [f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"]
    result = model.generate(prompts=prompts)
    return result.generations[0][0].text

# Render Document Preview
def render_document_preview(uploaded_file):
    reader = PdfReader(uploaded_file)
    all_text = "\n".join([reader.pages[i].extract_text() for i in range(len(reader.pages))])

    st.markdown("### 📖 Document Preview:")
    st.text_area(
        "Preview of the document (first 500 characters):",
        value=all_text[:500],
        height=150,
        disabled=True
    )
    st.sidebar.info(f"📄 Total Pages: {len(reader.pages)}")

# Chat Tab Functionality
def chat_tab(index, uploaded_file):
    query = st.text_input("💬 Enter your question:")

    col1, col2 = st.columns(2)
    with col1:
        submit = st.button("Submit")
    with col2:
        clear = st.button("Clear Answer")

    if clear:
        st.session_state["current_query"] = ""
        st.session_state["current_answer"] = ""

    if submit:
        if not uploaded_file:
            st.error("Please upload a PDF file first.")
        elif not query.strip():
            st.error("Query cannot be empty.")
        else:
            # Prevent answering the same query twice by checking history
            existing_entry = next((entry for entry in st.session_state["query_history"] if entry["query"] == query), None)
            
            if existing_entry:
                st.session_state["current_query"] = query
                st.session_state["current_answer"] = existing_entry["answer"]
            else:
                pinecone_results = query_pinecone(index, query)
                context = "\n".join([match["metadata"]["text"] for match in pinecone_results["matches"]])

                try:
                    generated_answer = generate_answer(context, query)
                    
                    # Store the new answer in history
                    st.session_state["current_query"] = query
                    st.session_state["current_answer"] = generated_answer
                    st.session_state["query_history"].append({"query": query, "answer": generated_answer})

                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    if st.session_state["current_answer"]:
        st.markdown("### 📜 Your Answer:")
        st.write(st.session_state["current_answer"])


# Document Details Tab
def document_details_tab(uploaded_file):
    if uploaded_file:
        st.markdown("### Document Details:")
        st.write(f"**File Name:** {uploaded_file.name}")
        st.write(f"**File Size:** {uploaded_file.size / 1024:.2f} KB")
        if "chunk_count" in st.session_state:
            st.write(f"**Indexed Chunks:** {st.session_state['chunk_count']}")
        else:
            st.warning("Document has not been processed yet.")
    else:
        st.warning("No document uploaded.")

# Query History Tab
def query_history_tab():
    st.markdown("### 📝 Query History")
    if "query_history" in st.session_state and st.session_state["query_history"]:
        for idx, entry in enumerate(st.session_state["query_history"], start=1):
            st.write(f"**Query {idx}:** {entry['query']}")
            st.write(f"**Answer {idx}:** {entry['answer']}")
            st.markdown("---")
    else:
        st.info("No queries have been made yet.")

# Main Application
def main():
    setup_streamlit_page()
    index = initialize_pinecone()

    uploaded_file = handle_file_upload(index)
    if uploaded_file:
        render_document_preview(uploaded_file)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📄 Chat", "📜 Document Details", "📝 Query History"])
    with tab1:
        chat_tab(index, uploaded_file)
    with tab2:
        document_details_tab(uploaded_file)
    with tab3:
        query_history_tab()

if __name__ == "__main__":
    main()