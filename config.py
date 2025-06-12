AUTHOR_CHAINLIT="PMAssist"
WELCOME_MESSAGE="""
👋 **Hi there! I'm PMAssist**, your AI-powered assistant for navigating internal project documentation.

Here's how I can help you:
- 🔍 **Quickly find** internal reports, meeting notes, and guidelines  
- 📂 **Navigate large sets** of documents with ease  
- ⚠️ **Flag outdated or missing information** in project records  
- 🧭 **Recommend and list documents** to relevant teams  
- ✍️ **Help draft** summaries, onboarding guides, or templates  
- 📚 **Index and organize** knowledge for future access

⏱️ **Save time. Reduce workload. Improve accuracy.**

**What can I help you with today?**
"""
from dotenv import load_dotenv
import os
os.environ.pop("CHROMA_DB_NAME")
load_dotenv()
CHROMA_DB_NAME = os.environ.get("CHROMA_DB_NAME")
DOCUMENT_YEAR_OLD_THRESHOLD=0