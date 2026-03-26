# RAG Document Chatbot

A conversational AI app that lets you upload any PDF and ask natural language 
questions about its contents. Built using Retrieval-Augmented Generation (RAG) 
to ground answers in your actual document rather than model hallucination.

## Demo

<img width="1142" height="1135" alt="image" src="https://github.com/user-attachments/assets/f2f76d46-1af9-492c-b035-ee8d3bf30cb1" />

## How it works

1. Upload any PDF document
2. The app chunks the text and converts it into vector embeddings using HuggingFace
3. Embeddings are stored in a FAISS vector database
4. When you ask a question, the app retrieves the most relevant chunks
5. LLaMA2 reads those chunks and generates a grounded answer

## Tech Stack

- **LangChain** — RAG pipeline orchestration
- **FAISS** — vector similarity search
- **HuggingFace Embeddings** — sentence-transformers/all-MiniLM-L6-v2
- **LLaMA2 via Ollama** — local LLM inference, no API costs
- **Streamlit** — interactive web interface
- **PyPDF** — PDF text extraction

## Setup

1. Install Ollama from https://ollama.com and run:




