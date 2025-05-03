import os
import time
import pickle
from typing import List, Any
from flask import Flask, request, jsonify
from datetime import datetime

# Initialize Flask app


import PyPDF2
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import create_retrieval_chain, create_stuff_documents_chain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.text_splitter import TokenTextSplitter
from langchain.schema import HumanMessage, AIMessage
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_google_genai import ChatGoogleGenerativeAI


app = Flask(__name__)

# Config
CACHE_DIR = "cache"
CHROMA_INDEX_DIR = os.path.join(CACHE_DIR, "chroma_index")
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

from pymongo import MongoClient
from datetime import datetime

# Connect to local MongoDB (adjust URI for Atlas or other setups)
client = MongoClient("mongodb://localhost:27017/")
db = client["nlp_bot_db"]
collection = db["query_logs"]



def extract_text_from_pdf(pdf_file_path: str) -> str:
    """Extract text from a PDF file."""
    text = ""
    try:
        with open(pdf_file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text


def preprocess_pdf(pdf_file_path: str) -> List[Document]:
    """Preprocess PDF file into Document format."""
    text = extract_text_from_pdf(pdf_file_path)
    documents = []
    if text:
        metadata = {
            "source": pdf_file_path,
            "type": "clinical-report"
        }
        documents.append(Document(page_content=text, metadata=metadata))
    return documents




def split_documents(documents: List[Document]) -> List[Document]:
    text_splitter = TokenTextSplitter(
        chunk_size=CHUNK_SIZE,  # usually ~500 tokens
        chunk_overlap=CHUNK_OVERLAP
    )

    chunks = []
    for doc in documents:
        if not doc.page_content.strip():
            continue
        try:
            split = text_splitter.split_documents([doc])
            for chunk in split:
                if chunk.page_content.strip():
                    chunks.append(chunk)
        except Exception as e:
            print(f"Error splitting document: {e}")
    return chunks


def save_to_cache(file_path: str, data: Any) -> None:
    try:
        with open(file_path, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Error saving to cache {file_path}: {e}")


def load_from_cache(file_path: str) -> Any:
    try:
        with open(file_path, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading from cache {file_path}: {e}")
        return None


def initialize_retriever():
    """Initialize or load Chroma vector store based on cache status"""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    if os.path.exists(CHROMA_INDEX_DIR):
        try:
            print("Loading Chroma index from cache...")
            vectorstore = Chroma(persist_directory=CHROMA_INDEX_DIR, embedding_function=embeddings)
            return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})
        except Exception as e:
            print(f"Error loading Chroma index: {e}, rebuilding...")

    # If we get here, we need to rebuild the index
    pdf_file_path = "clinical.pdf"
    print("Processing documents and building Chroma index...")

    preprocessed_docs = preprocess_pdf(pdf_file_path)
    chunked_docs = split_documents(preprocessed_docs)
    chunked_docs = [doc for doc in chunked_docs if doc.page_content.strip()]

    print(f"Number of non-empty document chunks: {len(chunked_docs)}")
    if not chunked_docs:
        raise ValueError("No valid content found in the document. Please check the input file.")

    # Create and save new index
    vectorstore = Chroma.from_documents(chunked_docs, embedding=embeddings, persist_directory=CHROMA_INDEX_DIR)
    vectorstore.persist()

    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})


def generate_response_with_memory(query, rag_chain, chat_history):
    try:
        response = rag_chain.invoke({"input": query, "chat_history": chat_history})
        answer = response.get("answer", "I couldn't find an answer.")
        retrieved_docs = response.get("context", [])

        source_map = {}
        for doc in retrieved_docs:
            url = doc.metadata.get("url", "")
            title = doc.metadata.get("report_title", "Untitled Report")
            if url:
                source_map[url] = title

        citations = ""
        if source_map:
            citations = "\n\n**Sources:**\n" + "\n".join(f"- [{title}]({url})" for url, title in source_map.items())

        full_response = f"{answer}\n\n{citations}"

        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=full_response))

        return full_response
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Error generating response"


def initialize_rag_system():
    print("Initializing RAG system...")
    start_time = time.time()

    retriever = initialize_retriever()
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp", temperature=0.3, max_tokens=500, timeout=120)

    contextualize_q_prompt = ChatPromptTemplate.from_messages([
        ("system", "Given a chat history and the latest user question, reformulate it as a standalone question."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ])

    history_aware_retriever = create_history_aware_retriever(model, retriever, contextualize_q_prompt)

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are a research assistant analyzing clinical reports. Always:\n"
         "1. Base answers on provided context\n"
         "2. Mention report titles\n"
         "3. Cite sources\n"
         "4. If unsure, say 'Based on available reports...'\n\n"
         "Context:\n{context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ])

    question_answer_chain = create_stuff_documents_chain(model, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    print(f"RAG initialization completed in {time.time() - start_time:.2f} seconds")
    return rag_chain


# Initialize at runtime
rag_chain = initialize_rag_system()


@app.route('/query', methods=['POST'])
def query():
    try:
        # Get query from the request
        data = request.get_json()
        query_input = data.get('query')
        if not query_input:
            return jsonify({"error": "Query input is missing"}), 400

        # Get the chat history (if provided)
        chat_history = data.get('chat_history', [])

        # Call the RAG system to get the response
        response = generate_response_with_memory(query_input, rag_chain, chat_history)

        # Store in MongoDB
        collection.insert_one({
            "query": query_input,
            "response": response,
            "chat_history": chat_history,
            "timestamp": datetime.utcnow()
        })

        # Return the response in JSON format
        return jsonify({"response": response}), 200

    except Exception as e:
        print(f"Error handling query: {e}")
        return jsonify({"error": "Internal server error"}), 500



if __name__ == '__main__':
    app.run(debug=True)
