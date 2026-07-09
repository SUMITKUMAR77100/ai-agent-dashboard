# 🤖 AI Agent Dashboard
### Week 3 Final Project — ReAct Agent + Context Management

## Stack
- **Backend**: FastAPI + Groq (Llama 3.1 8B) + tiktoken
- **Frontend**: React + react-markdown
- **Agent**: ReAct pattern (Reason → Act → Observe → Repeat)
- **Tools**: web_search, calculator, document_retrieval
- **Context**: Auto-summarises when history exceeds 10K tokens

## Run

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
cp .env.example .env       # Add your GROQ_API_KEY
export TMPDIR=/tmp
python -m uvicorn main:app --reload --port 8080
```

### Frontend
```bash
cd frontend
npm install
npm start
```

Open http://localhost:3000

## Features
- 🧠 Agent thinking sidebar — see every tool call + result
- 📊 Stats: questions asked, tool calls made, tokens used
- ⚡ Context summarisation when history gets too long
- 🔍 Quick question buttons for instant demos
- 3 Tools: web search, calculator, document retrieval
