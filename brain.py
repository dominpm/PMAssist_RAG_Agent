import os
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import chromadb
from langchain.globals import set_debug

# set_debug(True)

def load_rag_chain(collection_name: str) -> RetrievalQA:
    # Load API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("Missing GOOGLE_API_KEY in environment.")

    # Gemini LLM with streaming
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        callbacks=[StreamingStdOutCallbackHandler()]
    )

    # Embedding model
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # Load Chroma running locally
    client = chromadb.HttpClient(host="localhost", port=8000)

    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embedding,
        client=client
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

    # Create a RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        return_source_documents=True
    )

    return qa_chain

from typing import List, Dict, Literal, Union
def ask_brain(question: str, collection_name="PMAssist") -> Dict[Union[Literal["text"], Literal["sources"]], Union[str, List[Dict[Union[Literal["source"], Literal["page"]], str]]]]:
    """
    Runs the RAG pipeline with a user question and streams the answer.
    """
    # print(f"\n🧠 Asking: {question}\n")
    rag = load_rag_chain(collection_name=collection_name)
    response = rag.invoke({"query": question})
    sources = [{
           "source" : doc.metadata.get('source'),
           "page" : doc.metadata.get('page'),
           "text": doc.page_content,
           "metadata" : doc.metadata
       } for doc in response["source_documents"]]
    # print(sources)
    return {
       "text" : response["result"],
       "sources" : sources
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(ask_brain(" ".join(sys.argv[1:])))
    else:
        q = input("Ask a question: ")
        print(ask_brain(q, collection_name="PMAssist_v2"))
