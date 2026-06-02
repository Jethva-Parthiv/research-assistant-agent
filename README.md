# Research-Assistant-Agent

AI-powered Research Assistant Agent built using:

- LangGraph
- LangChain
- Google Gemini (via `langchain-google-genai`)
- Tavily Search API

This project implements an **agentic research workflow** that:

- rewrites the user query for better web search
- plans multiple research tasks
- searches the web and gathers evidence per task
- synthesizes a final grounded answer
- returns the final response as structured markdown (per prompt)

---

# Features

## Current Features

- AI-powered research assistant
- Query rewriting for search optimization
- Task planning for multi-step research
- Web search + webpage extraction via Tavily
- Evidence-based answer synthesis
- Deep (workflow-based) orchestration with LangGraph
- Modular architecture (nodes/services/agents)

---

# Project Architecture

```text
User Query
  ↓
query_rewrite_node (rewrite for search)
  ↓
planner_node (create research tasks)
  ↓
evidence_node (search + gather evidence)
  ↓
synthesis_context (synthesize final answer)
  ↓
END
```

---

# Tech Stack

- Python
- LangGraph
- LangChain
- Google Gemini
- Tavily Search API

---

# Folder Structure (approx.)

```text
Research_Assisatant_Agent/
│
├── app/
│   ├── core/
│   │   ├── logging.py
│   │   └── settings.py
│   │
│   ├── agents/
│   │   ├── classifier.py
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   └── synthesizer.py
│   │
│   ├── graph/
│   │   ├── state.py
│   │   ├── builder.py
│   │   └── workflows/
│   │       ├── research_router.py
│   │       ├── deep_research.py
│   │       └── simple_research.py
│   │
│   ├── graph/nodes/
│   │   ├── query_rewrite_node.py
│   │   ├── planner_node.py
│   │   ├── evidence_node.py
│   │   ├── synthesis_context.py
│   │   ├── search_node.py
│   │   ├── extract_node.py
│   │   ├── formatter_node.py
│   │   ├── answer_node.py
│   │   └── router_node.py
│   │
│   ├── ingestion/
│   │   ├── chunking.py
│   │   └── ingest.py
│   │
│   ├── memory/
│   │   └── postgres_memory.py
│   │
│   ├── prompts/
│   │   └── research_prompt.py
│   │
│   ├── services/
│   │   ├── citation.py
│   │   ├── formatter.py
│   │   ├── query_rewriter.py
│   │   └── document_saver.py
│   │
│   ├── tools/
│   │   └── web_search.py
│   │
├── .env
├── requirements.txt
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/Jethva-Parthiv/research-assistant-agent.git
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

# Current Workflow (router selects workflow)

This repo supports **two LangGraph pipelines**. A `router` node classifies the query and then runs either:

- **deep** (`deep_research`)
- **simple** (`simple_research`)

---

# Deep Workflow (deep_research)

```text
query_rewrite_node → planner_node → evidence_node → synthesis_context → END
```

---

# Simple Workflow (simple_research)

```text
query_rewrite_node → search_node → extract_node → formatter_node → answer_node → END
```



---

# Future Improvements

Planned features:

- PDF/document ingestion
- Vector databases / persistent RAG storage
- Conversational memory
- Multi-agent collaboration patterns
- Async + streaming responses
- Reranking and retrieval evaluation
- FastAPI backend
- Web UI

---

# Learning Goals

This project focuses on understanding:

- Agentic AI
- LangGraph workflows
- Retrieval-Augmented Generation (RAG)
- grounded synthesis with evidence
- AI orchestration
- tool calling (web search + extraction)
- scalable agent architecture

---

# Author

Built for learning and research in modern AI engineering and agentic systems.

