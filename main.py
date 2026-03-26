import os
import shutil
import streamlit as st
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_classic.memory import ConversationBufferMemory


# Create a folder that stores out vector database locally.
vector_space_dir = os.path.join(os.getcwd(), "vector_db")
if not os.path.exists(vector_space_dir):
    os.mkdir(vector_space_dir)

# Sets up the UI, showing tab title and main heading. 
st.set_page_config(page_title="RAG ChatBot")
st.title("RAG ChatBot (Langchain + LLaMA2)")

if 'vectorstore' not in st.session_state:
    st.session_state['vectorstore'] = None
if 'memory' not in st.session_state:
    st.session_state['memory'] = ConversationBufferMemory(memory_key = "chat_history", return_messages=True)
if 'retriever' not in st.session_state:
    st.session_state['retriever'] = None


# Displays a pdf that lets the user upload pdf. Once uplaoded, we use HuggingFaceEmbeddings to convert chunks of the pdf into vectors. 
upload_pdf = st.file_uploader("Upload PDF here", type=["pdf"])
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


if upload_pdf is not None and st.session_state.get('vectorstore') is None:
    with st.spinner("Creating vector DB..."):
        # Upload PDF To disk
        pdf_path = os.path.join(os.getcwd(), upload_pdf.name)
        with open(pdf_path, "wb") as f:
            f.write(upload_pdf.getbuffer())
        st.session_state['pdf_path'] = pdf_path
        # Load the pdf using PyPDFLoader and split it into chunks
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        # Save these vectors in FAISS (our Vector DB)
        vectorstore = FAISS.from_documents(documents, embedding_model)
        vectorstore.save_local(vector_space_dir)
        # Stores the retriever and vector DB in st.session_state so that we can refer to it later in the chat. 
        st.session_state['vectorstore'] = vectorstore
        st.session_state['retriever'] = vectorstore.as_retriever(search_kwargs={"k": 3})
        st.success("Vector DB created successfully!")


# Initializes the LLaMA2 model that will be used to answer the user's questions. 
llm = OllamaLLM(model = "llama2")

if st.session_state.get('retriever'):
    # Ties the memory, retriever, and LLM together in one fluid chat system
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm = llm,
        retriever = st.session_state['retriever'],
        memory = st.session_state['memory']
    )
    
    # When the user types a question:
    #     1. Searches the vector DB
    #     2. Sends the context and quesion to LLaMA2
    #     3. Displays the generated answer in the chat

    user_question = st.text_input("Ask a question:")
    if user_question:
        with st.spinner("Thinking..."):
            result = qa_chain.run({"question":user_question})
            st.markdown(f"**You:** {user_question}")
            st.markdown(f"**Bot:** {result}")

# helper functions to delete the saved vector DB and uploaded pdf if the user wants to start over. 
def del_vectordb(path):
    if os.path.exists(path):
        shutil.rmtree(path)

def del_uploaded_pdf(path):
    if path and os.path.exists(path):
        os.remove(path)

# reset button
if st.button("Clear Session"):
    st.session_state['memory'].clear()
    st.session_state['retriever'] = None
    st.session_state['vectorstore'] = None
    del_vectordb(vector_space_dir)
    pdf_p = st.session_state.get('pdf_path', None)
    del_uploaded_pdf(pdf_p)
    st.session_state['pdf_file_path'] = None
    for key in ['upload_pdf', 'text']:
        if key in st.session_state:
            del st.session_state[key]
    st.success('Session, PDF and VectorDB are cleared')
    st.rerun()