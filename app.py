from chainlit import on_message, on_chat_start, Message, Pdf, Step
from config import AUTHOR_CHAINLIT, WELCOME_MESSAGE, CHROMA_DB_NAME, DOCUMENT_YEAR_OLD_THRESHOLD
from brain import ask_brain
from typing import List
import os

@on_message
async def on_message(message : Message):
    stream_message = Message(content="", author=AUTHOR_CHAINLIT)
    
    #generate response
    async with Step(name="Searching internal documentation", default_open=True) as step: 
        response = ask_brain(question=message.content,
                            collection_name=CHROMA_DB_NAME)
    
    # await step.remove() # I want to show the rag retrieved chunks from it
    await stream_message.stream_token(
        response["text"]
    )
    
    # print the document for each doc, gather pdfs firt
    elements = []
    markdown_sources, old_sources, old_sources_ls = parse_sources_to_markdown(response["sources"])
    await step.stream_token(
        markdown_sources
    )
    if old_sources:
        text = "\n\n"
        text+="### ⚠️ WARNING ⚠️"
        docs_names = set([os.path.splitext(doc.get("source", "Unknown Source"))[0] for doc in old_sources_ls])
        for doc in docs_names:
            text += f"\n - The document {doc}  is more than {DOCUMENT_YEAR_OLD_THRESHOLD} years old."
        await stream_message.stream_token(text)
    cleaned_docs : List[str] = list(set([source["source"] for source in response["sources"]]))
    for source in cleaned_docs:
        elements.append(Pdf(
            path=os.path.join("./data", source),
        ))
    stream_message.elements = elements
    await stream_message.send()
    
@on_chat_start
async def on_chat_start():
    welcome_message = Message(content=WELCOME_MESSAGE, author=AUTHOR_CHAINLIT)
    await welcome_message.send()
    
    
    
def parse_sources_to_markdown(sources) -> tuple[str, bool, List]:
    old_sources = False
    markdown = "### 📚 Retrieved Sources\n\n"
    old_sources_ls = []
    for i, src in enumerate(sources, 1):
        title = src.get("source", "Unknown Source")
        page = src.get("page", "N/A")
        text = src.get("text", "").strip()
        metadata = src.get("metadata", {})
        
        markdown += f"#### {i}. **{title}** (Page {page}/{metadata["total_pages"]})\n"
        markdown += f"##### Creation date : {format_date(metadata["creationdate"])}\n"
        markdown += f"##### Last modification date : {format_date(metadata["moddate"])}\n\n"
        if passes_threshold_of_document_expiry(metadata["moddate"]):
            old_sources=True
            markdown += f"#### ⚠️ WARNING ⚠️ : This document is more than {DOCUMENT_YEAR_OLD_THRESHOLD} years old. \n\n"
            old_sources_ls.append(src)
        markdown += f"{text}\n\n"
        markdown += "---\n\n"

    return markdown, old_sources, old_sources_ls

from datetime import datetime, timedelta

def format_date(date_str: str) -> str:
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%B %d, %Y %I:%M %p")
    except (ValueError, TypeError):
        return "Unknown"

def passes_threshold_of_document_expiry(moddate_str : str) -> bool:
    try:
        mod_date = datetime.fromisoformat(moddate_str)
        current_date = datetime.now(mod_date.tzinfo)
        return (current_date - mod_date) > timedelta(days=365*DOCUMENT_YEAR_OLD_THRESHOLD)
    except (ValueError, TypeError):
        return False