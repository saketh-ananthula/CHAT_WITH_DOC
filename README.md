# CHAT_WITH_DOC

This project is a Streamlit web application that allows users to upload PDF documents, index their contents using Pinecone, and interact with the documents by asking questions. The application leverages LangChain for embedding generation, Google Generative AI (Gemini) for answering queries, and Pinecone for vector storage and retrieval.

---

## Features

- 📂 **Upload PDF Documents**: Users can upload PDF files to the application.
- 📤 **Document Indexing**: Extracts text from the uploaded PDF and indexes it into Pinecone.
- 💬 **Ask Questions**: Users can ask questions about the document's content and get answers.
- 📝 **Query History**: Keeps track of all queries and their respective answers.
- 📜 **Document Preview**: Displays the first 500 characters of the document as a preview.
- 🔒 **Session Management**: Caches uploaded documents and indexed data for better performance.

---

## Technologies Used

- **Python**: Core programming language.
- **Streamlit**: Web framework for building interactive UIs.
- **Pinecone**: Vector database for document indexing and retrieval.
- **LangChain**: Framework for handling embeddings and chunking.
- **PyPDF2**: Library for extracting text from PDFs.
- **Google Generative AI (Gemini)**: Used to generate answers based on the retrieved document context.
- **dotenv**: For securely managing environment variables.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/your-repo-name.git
   cd your-repo-name
   ```

2. Create and activate a virtual environment (optional):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the project root and add the following keys:
   ```env
   PINECONE_API_KEY=<your_pinecone_api_key>
   GOOGLE_API_KEY=<your_google_api_key>
   INDEX_NAME=<your_pinecone_index_name>
   ```

5. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

---

## Usage

1. **Upload Document**:
   - Navigate to the sidebar and upload a PDF file.
   - The document will be processed and indexed into Pinecone.

2. **Ask Questions**:
   - Enter your query in the text input field under the "Chat" tab and press "Submit".
   - The application retrieves relevant document chunks and generates an answer.

3. **View Document Details**:
   - Switch to the "Document Details" tab to view metadata about the uploaded document.

4. **Review Query History**:
   - Switch to the "Query History" tab to see past queries and their answers.

---

## File Structure

```plaintext
├── app.py                # Main application code
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (ignored in Git)
├── README.md             # Project documentation
└── ...                   # Other files
```

---

## Dependencies

- Python >= 3.7
- Streamlit
- PyPDF2
- Pinecone
- LangChain
- Google Generative AI SDK
- dotenv

---

## Known Issues

- **File Size Limit**: Ensure uploaded PDFs are within the maximum allowed size for efficient processing.
- **API Limits**: Query responses are subject to Pinecone and Google Generative AI API limits.

---

## Future Enhancements

- Support for additional file formats (e.g., DOCX, TXT).
- Improved error handling and logging.
- Integration with other LLMs and embedding models.
- Enhanced UI with better document navigation and search options.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## Author

Developed by [SAKETH ANANTHULA](https://github.com/saketh-ananthula).
