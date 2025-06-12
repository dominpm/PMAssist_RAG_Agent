import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import chromadb
from config import CHROMA_DB_NAME

def ingest_pdfs_to_chroma(pdf_dir: str = "./data"):
    """
    Load PDFs from a directory, embed them using Gemini, and insert into ChromaDB running locally.
    Each chunk includes metadata (filename, page number).
    """

    # Step 1: Load PDFs
    all_docs = []
    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            path = os.path.join(pdf_dir, filename)
            loader = PyPDFLoader(path)
            docs = loader.load()

            # Add source metadata
            for doc in docs:
                doc.metadata["source"] = filename
            all_docs.extend(docs)

    if not all_docs:
        raise ValueError("No PDF documents found.")

    # Step 2: Split text into chunks, preserving metadata
    splitter = RecursiveCharacterTextSplitter(chunk_size=4098, chunk_overlap=512)
    split_docs = splitter.split_documents(all_docs)

    # Step 3: Initialize Gemini embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Step 4: Connect to local Chroma instance    
    vectordb = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        client=chromadb.HttpClient(host="localhost", port=8000),
        collection_name=CHROMA_DB_NAME
    )

    
    print(f"✅ Ingested {len(split_docs)} chunks with metadata into Chroma")
    return vectordb

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    ingest_pdfs_to_chroma()