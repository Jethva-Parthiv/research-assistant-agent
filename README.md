# Research-Assistant-Agent

AI-powered Research Assistant Agent built using:

- LangGraph
- LangChain
- Gemini
- Tavily Search API

RAGSearch_AI is an agentic AI system capable of:

- web search
- reasoning over retrieved information
- grounded response generation
- citation generation
- workflow-based AI orchestration

The project is designed as a scalable foundation for future:

- Retrieval-Augmented Generation (RAG)
- multi-agent systems
- conversational memory
- document ingestion
- enterprise AI workflows

---

# Features

## Current Features

- AI-powered research assistant
- Web search integration using Tavily
- LangGraph workflow orchestration
- Gemini-powered reasoning
- Citation-grounded responses
- Modular architecture
- Production-style project structure

---

# Project Architecture

```text
User Query
    ↓
Web Search Tool
    ↓
Retrieved Results
    ↓
LLM Reasoning
    ↓
Grounded Answer + Citations
```

---

# Tech Stack

- Python
- LangGraph
- LangChain
- Google Gemini
- Tavily Search API

---

# Folder Structure

```text
RAGSearch_AI/
│
├── app/
│   ├── agents/
│   │   └── researcher.py
│   │
│   ├── graph/
│   │   ├── builder.py
│   │   └── state.py
│   │
│   ├── tools/
│   │   └── web_search.py
│   │
│   ├── prompts/
│   │
│   └── main.py
│
├── .env
├── requirements.txt
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/your-username/RAGSearch_AI.git
cd RAGSearch_AI
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux/Mac

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install langgraph
pip install langchain
pip install langchain-google-genai
pip install tavily-python
pip install python-dotenv
```

---

# Environment Variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key
TAVILY_API_KEY=your_api_key
```

---

# Run Project

```bash
python -m app.main
```

---

# Example Query

```text
What is Retrieval-Augmented Generation?
```

---

# Current Workflow

```text
search_node
    ↓
answer_node
    ↓
END
```

---

# Future Improvements

Planned features:

- RAG pipelines
- PDF/document ingestion
- vector databases
- conversational memory
- multi-agent workflows
- async processing
- query rewriting
- reranking
- streaming responses
- FastAPI backend
- web UI

---

# Learning Goals

This project focuses on understanding:

- Agentic AI
- LangGraph workflows
- Retrieval-Augmented Generation
- grounded generation
- AI orchestration
- tool calling
- citation generation
- scalable AI architecture

---

# Author

Built for learning and research in modern AI engineering and agentic systems.