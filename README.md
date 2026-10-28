# Chat with Multiple PDFs

A Streamlit application for asking questions across uploaded PDF documents. It extracts text, splits it into chunks, creates a local FAISS vector index using Hugging Face sentence embeddings, and uses a Groq-hosted language model to answer follow-up questions.

## Features

- Upload and process multiple PDFs in one session
- Extract text from text-based PDFs with pypdf
- Chunk text for semantic retrieval
- Build a FAISS vector index using `sentence-transformers/all-MiniLM-L6-v2`
- Conversational question answering using LangChain and Groq
- Local Streamlit interface

## Requirements

- Python 3.10+ recommended; use a version compatible with the installed LangChain and ML dependencies
- A Groq API key
- Internet access for the hosted model and initial embedding-model download
- Text-based PDFs; scanned PDFs require OCR, which is not currently included

## Setup

Clone the repository:

```bash
git clone https://github.com/muneerahmedkhokhar53-wq/Chat_with_multiple_PDFs_using_LangChain_Groq_and_Streamlit.git
cd Chat_with_multiple_PDFs_using_LangChain_Groq_and_Streamlit
python -m venv .venv
```

Activate the environment.

**Windows PowerShell**
```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create a local `.env` file from the example and add your own API key:

**Windows**
```powershell
Copy-Item .env.example .env
```

**macOS / Linux**
```bash
cp .env.example .env
```

Edit `.env` and set `GROQ_API_KEY` to your own key. Never commit a real API key or a populated `.env` file.

## Run

```bash
python -m streamlit run app.py
```

Open the local address printed by Streamlit. Upload one or more PDFs in the sidebar, click **Process**, then ask a question about the documents.

## How it works

1. **Extraction:** pypdf reads text from each uploaded PDF.
2. **Chunking:** text is divided into overlapping chunks.
3. **Embeddings:** a Hugging Face sentence-transformer maps chunks to vectors.
4. **Retrieval:** FAISS selects relevant chunks.
5. **Generation:** a Groq-hosted model answers within the conversational retrieval chain.

## Limitations and responsible use

- Scanned or image-only PDFs may yield no text because OCR is not implemented.
- The application currently combines extracted PDF text into a shared text collection; document-level source citations and page-level provenance are not surfaced in the UI.
- The language model can produce incorrect or unsupported answers. Verify important claims against the original PDFs.
- Uploaded documents may contain sensitive information. Use only documents you are authorized to process and consider the external model provider's data-handling terms before submitting content.
- Embedding-model downloads may require internet access on first run.
- Dependencies are currently declared without version pins. For reproducible installations, record and test a compatible dependency set.

## Security

The application should be run locally for personal experimentation unless you add authentication, upload-size limits, deployment hardening, and a clear data-retention policy. Chat content is escaped before it is inserted into the custom HTML chat template.

## License

Check the repository for a license file before redistributing or reusing this project.
