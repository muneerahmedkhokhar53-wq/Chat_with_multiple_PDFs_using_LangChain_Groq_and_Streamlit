"""Streamlit PDF question-answering app with source-aware retrieval."""

from __future__ import annotations

import os
from io import BytesIO
from typing import Iterable

import streamlit as st
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_CHAT_MODEL = "llama-3.3-70b-versatile"
MAX_PDF_SIZE_MB = 25
MAX_PDF_COUNT = 20


def extract_pdf_documents(pdf_files: Iterable) -> list[Document]:
    """Extract text page-by-page and retain source metadata for citations."""
    documents: list[Document] = []
    for pdf_file in pdf_files:
        file_name = getattr(pdf_file, "name", "uploaded.pdf")
        file_bytes = pdf_file.getvalue()
        if not file_bytes:
            st.warning(f"'{file_name}' is empty and was skipped.")
            continue

        try:
            reader = PdfReader(BytesIO(file_bytes), strict=False)
            for page_number, page in enumerate(reader.pages, start=1):
                page_text = (page.extract_text() or "").strip()
                if page_text:
                    documents.append(
                        Document(
                            page_content=page_text,
                            metadata={
                                "source": file_name,
                                "page": page_number,
                            },
                        )
                    )
        except Exception as exc:
            st.warning(f"Could not read '{file_name}': {exc}")

    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    """Split each page while preserving its document and page metadata."""
    if not documents:
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=180,
        separators=["\n\n", "\n", ". ", " ", ""],
        add_start_index=True,
    )
    return splitter.split_documents(documents)


@st.cache_resource(show_spinner="Loading the embedding model...")
def load_embeddings() -> HuggingFaceEmbeddings:
    """Load and cache the local sentence-transformer model."""
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def build_vector_store(chunks: list[Document]) -> FAISS:
    if not chunks:
        raise ValueError("No readable text was found in the uploaded PDFs.")
    return FAISS.from_documents(chunks, load_embeddings())


def build_conversation_chain(vector_store: FAISS) -> ConversationalRetrievalChain:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is missing. Add it to your .env file or deployment secrets."
        )

    llm = ChatGroq(
        model=DEFAULT_CHAT_MODEL,
        api_key=api_key,
        temperature=0.2,
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )
    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(search_kwargs={"k": 4}),
        memory=memory,
        return_source_documents=True,
        output_key="answer",
        verbose=False,
    )


def format_sources(source_documents: list[Document]) -> list[str]:
    """Return unique, human-readable source labels."""
    sources: list[str] = []
    seen: set[tuple[str, int | str]] = set()
    for document in source_documents:
        source = str(document.metadata.get("source", "Unknown document"))
        page = document.metadata.get("page", "?")
        key = (source, page)
        if key not in seen:
            seen.add(key)
            sources.append(f"{source} — page {page}")
    return sources


def render_chat() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("Sources"):
                    for source in message["sources"]:
                        st.caption(f"• {source}")


def process_question(question: str) -> None:
    chain = st.session_state.get("conversation")
    if chain is None:
        st.warning("Upload and process your PDFs before asking a question.")
        return

    st.session_state.messages.append({"role": "user", "content": question})
    try:
        with st.spinner("Searching your documents and preparing an answer..."):
            result = chain.invoke({"question": question})
        answer = result.get("answer", "I couldn't generate an answer.")
        sources = format_sources(result.get("source_documents", []))
        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )
    except Exception as exc:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    "I couldn't complete that request. Check your Groq API key, "
                    "network connection, and model availability, then try again. "
                    f"\n\nTechnical detail: {exc}"
                ),
                "sources": [],
            }
        )


def main() -> None:
    st.set_page_config(
        page_title="PDF Research Assistant",
        page_icon="📚",
        layout="wide",
    )
    st.title("📚 PDF Research Assistant")
    st.caption(
        "Ask questions across your documents. Answers include source-file and page references."
    )

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.sidebar:
        st.header("Document library")
        st.caption("Upload up to 20 text-based PDFs (25 MB each).")
        pdf_files = st.file_uploader(
            "Choose PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            help="Scanned/image-only PDFs are not OCR-processed.",
        )

        if st.button("Process documents", type="primary", use_container_width=True):
            if not pdf_files:
                st.warning("Choose at least one PDF first.")
            elif len(pdf_files) > MAX_PDF_COUNT:
                st.error(f"Please upload no more than {MAX_PDF_COUNT} PDFs.")
            elif any(file.size > MAX_PDF_SIZE_MB * 1024 * 1024 for file in pdf_files):
                st.error(f"Each PDF must be {MAX_PDF_SIZE_MB} MB or smaller.")
            else:
                with st.spinner("Extracting, chunking, and indexing documents..."):
                    page_documents = extract_pdf_documents(pdf_files)
                    chunks = split_documents(page_documents)
                    if not chunks:
                        st.error(
                            "No extractable text was found. These PDFs may be scanned "
                            "or image-only; OCR is not currently supported."
                        )
                    else:
                        try:
                            vector_store = build_vector_store(chunks)
                            st.session_state.conversation = build_conversation_chain(
                                vector_store
                            )
                            st.session_state.messages = []
                            st.success(
                                f"Indexed {len(pdf_files)} PDF(s) into {len(chunks)} chunks."
                            )
                        except Exception as exc:
                            st.error(f"Document processing failed: {exc}")

        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.conversation is not None:
                st.session_state.conversation.memory.clear()
            st.rerun()

        st.divider()
        st.caption("Privacy note")
        st.caption(
            "PDF text is sent to the configured Groq service when you ask a question. "
            "Do not upload confidential documents unless permitted by your data policy."
        )

    render_chat()
    question = st.chat_input("Ask a question about your processed PDFs...")
    if question:
        process_question(question)
        st.rerun()


if __name__ == "__main__":
    main()
