# 🤖 SuperBot — Enterprise AI Assistant

## Quick Start
```bash
cd SuperBot
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
streamlit run app.py
```

## Features
- 📊 **Dashboard** — Action cards, live chat with robot mascot
- 🎫 **Jira Tracker** — View/create/update issues, sprint board, natural language creation
- 👔 **HR Tasks** — Policy Q&A (RAG), leave balances, directory, announcements
- 🗄️ **Data Queries** — DW schema explorer, pipeline monitor, AI SQL generator
- 📚 **Knowledge Base** — Upload PDFs/docs → auto-indexed → source-cited answers
- 🔧 **Need Help?** — IT helpdesk ticket creation via chat
- ⚙️ **Admin Panel** — Analytics, MCP tools, audit log, conversation history, alerts
- ⚙️ **Settings** — Profile, integrations, export, RAG rebuild

## Architecture
```
RAG (NumPy vector store) + MCP Tool Registry + Groq LLM
         ↓                       ↓                ↓
  Document Search          Tool Dispatch      AI Responses
  Source Citations         Audit Logging     Intent Router
```
<img width="435" height="722" alt="image" src="https://github.com/user-attachments/assets/2aad1d73-1a7a-4d4f-9c00-a7940d692972" />



## Config
Edit `.env` — set `GROQ_API_KEY` from https://console.groq.com
