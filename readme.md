# Chat with Multiple PDFs 📚

A Streamlit app that lets you chat with multiple PDF documents using AI.
Upload your PDFs, click Process, and ask questions about your documents.

## Features
- Upload multiple PDFs at once
- Free AI responses powered by Groq (Llama 3.3)
- Free local embeddings via HuggingFace
- Conversation memory — ask follow-up questions

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/pdf-chat.git
cd pdf-chat
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API keys
Copy `.env.example` to `.env` and fill in your keys:
```
GROQ_API_KEY=gsk_your_groq_api_key_here
HUGGINGFACE_API_TOKEN=hf_your_huggingface_token_here
```

Get your free Groq API key at: https://console.groq.com

### 4. Run the app
```bash
streamlit run app.py
```

## Deploy on Streamlit Cloud
1. Push this repo to GitHub
2. Go to https://streamlit.io/cloud
3. Connect your GitHub repo
4. Add your API keys in Settings → Secret
5. Click Deploy

## Tech Stack
- Streamlit
- LangChain
- Groq (Llama 3.3 70B)
- HuggingFace Embeddings
- FAISS Vector Store
