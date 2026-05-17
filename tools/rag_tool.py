# tools/rag_tool.py
# ---------------------------------------------------------------
# RAG (Retrieval-Augmented Generation) Tool
# This tool embeds a PDF report into a FAISS vector store,
# then retrieves relevant chunks to answer questions about it.
# The agent calls this for questions about strategy, goals,
# policies, or anything that would be in a report document.
# ---------------------------------------------------------------

import os
from langchain.tools import tool
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

VECTORSTORE_PATH = "vectorstore/sales_report_index"
REPORT_PATH = "data/sales_report.txt"   # We use .txt fallback (no PDF needed)

_retriever = None  # cached so we don't re-embed every call


def build_or_load_vectorstore():
    """Build the FAISS index from document, or load existing one."""
    global _retriever

    if _retriever is not None:
        return _retriever

    embeddings = OpenAIEmbeddings()

    # Load existing index if already built
    if os.path.exists(VECTORSTORE_PATH):
        db = FAISS.load_local(VECTORSTORE_PATH, embeddings,
                              allow_dangerous_deserialization=True)
        _retriever = db.as_retriever(search_kwargs={"k": 4})
        return _retriever

    # Build fresh index from document
    loader = TextLoader(REPORT_PATH)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=80)
    chunks = splitter.split_documents(docs)

    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(VECTORSTORE_PATH)

    _retriever = db.as_retriever(search_kwargs={"k": 4})
    return _retriever


@tool
def query_sales_report(question: str) -> str:
    """
    Answer questions about the annual sales strategy report, 
    company goals, targets, regional strategy, and qualitative 
    business context. Use this for questions about 'why', 
    strategy, forecasts, or anything policy/goal related.
    
    Input: a natural language question about the report.
    Output: an answer based on the report content.
    """
    try:
        retriever = build_or_load_vectorstore()
        docs = retriever.get_relevant_documents(question)

        if not docs:
            return "No relevant information found in the sales report."

        context = "\n\n".join([d.page_content for d in docs])
        return f"Based on the sales report:\n\n{context}"

    except Exception as e:
        return f"Could not retrieve from report: {str(e)}"
