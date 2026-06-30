<div align="center">

# 🔬 Research Assistant Agent

**AI-Powered Deep Research with Automated Fact-Checking & Citation Verification**

[![Python](https://img.shields.io/badge/Python-≥3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2.5-1C3C3C?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Gemini](https://img.shields.io/badge/Google_Gemini-2.5_Flash-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)
[![Tavily](https://img.shields.io/badge/Tavily-Search_API-FF6F00)](https://tavily.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web_GUI-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

An agentic research system that autonomously plans research tasks, searches the web, gathers multi-source evidence, synthesizes grounded answers with citations, and **verifies every claim** against its source material — all orchestrated through a LangGraph state machine.

</div>

---

## ✨ Key Features

| Feature | Description |
|:---|:---|
| **Intelligent Query Routing** | An LLM classifier automatically routes queries to either a Fast or Deep research pipeline based on complexity |
| **Query Rewriting** | Rewrites user queries into search-optimized terminology before web retrieval |
| **Multi-Step Task Planning** | Decomposes complex queries into focused research sub-tasks via structured LLM output |
| **Web Search & Extraction** | Retrieves top results and scrapes full-page content using the Tavily Search + Extract API |
| **Evidence-Based Synthesis** | Compiles evidence per sub-task, analyzes trade-offs, compares viewpoints, and resolves conflicts |
| **Claim Verification Pipeline** | Extracts factual claims from the report, cross-verifies each against source passages, and assigns confidence scores |
| **Gap Analysis & Retry Loop** | Evaluates synthesis quality — if confidence is low, the system re-plans and gathers more evidence (up to 1 retry) |
| **Verified Report Assembly** | Generates a structured markdown report with inline verification badges (`✅ VERIFIED`, `⚠️ WEAK`, `❌ UNVERIFIED`) |
| **Dual Interface** | Full-featured **Streamlit Web GUI** with real-time workflow tracking, and a **Rich CLI** for terminal usage |
| **Export Options** | Export research reports as **PDF** or **Markdown** directly from the web GUI |
| **Research History** | Browse, reload, and delete past research sessions from the sidebar |

---

## 🏗️ Architecture Overview

The system is a **multi-workflow orchestrator** built on LangGraph. A top-level router classifies each query and delegates it to one of two dedicated pipelines:

```
                          ┌─────────────┐
                          │  User Query │
                          └──────┬──────┘
                                 │
                          ┌──────▼──────┐
                          │ Router Node │  ← LLM Classifier (SIMPLE / DEEP)
                          └──────┬──────┘
                                 │
                ┌────────────────┼────────────────┐
                │                                 │
       ┌────────▼────────┐              ┌─────────▼─────────┐
       │  Fast Research  │              │   Deep Research    │
       │    Pipeline     │              │     Pipeline       │
       └────────┬────────┘              └─────────┬─────────┘
                │                                 │
                ▼                                 ▼
         Quick factual                  Multi-step analytical
         lookup (5 nodes)               research (8+ nodes)
```

### Fast Research Pipeline

Optimized for quick, single-topic factual lookups:

```
query_rewrite → search → extract → formatter → answer → END
```

### Deep Research Pipeline

Designed for complex analysis requiring task decomposition, multi-source synthesis, and fact-checking:

```
query_rewrite → planner → evidence → synthesis
                                        │
                              ┌─────────▼──────────┐
                              │ Quality Evaluation  │
                              │  (confidence < 3.5  │
                              │   & retries < 1?)   │
                              └─────────┬──────────┘
                                 ┌──────┴──────┐
                           Yes   │             │  No
                    ┌────────────▼──┐   ┌──────▼────────┐
                    │ Gap Analysis  │   │ Claim Splitter │
                    │ → re-evidence │   │ → Verification │
                    └───────────────┘   │ → Report Build │
                                        └───────────────┘
```

> For a detailed walkthrough of every node, state field, and routing decision, see [`architecture.md`](./architecture.md).

---

## 🧩 Tech Stack

| Layer | Technology | Purpose |
|:---|:---|:---|
| **Orchestration** | [LangGraph](https://github.com/langchain-ai/langgraph) `1.2.5` | State-machine workflow engine with conditional edges and subgraphs |
| **LLM** | [Google Gemini](https://ai.google.dev/) via `langchain-google-genai` `4.2.5` | Query rewriting, planning, synthesis, classification, claim verification |
| **Web Search** | [Tavily](https://tavily.com) `0.7.24` | Search API + full-page text extraction |
| **Data Models** | [Pydantic](https://docs.pydantic.dev/) `2.13.4` | Structured LLM outputs, claim models, report models |
| **Web GUI** | [Streamlit](https://streamlit.io) `≥1.35.0` | Interactive research dashboard with live workflow tracking |
| **CLI** | [Rich](https://github.com/Textualize/rich) `15.0.0` | Terminal UI with spinners, markdown rendering, and styled panels |
| **PDF Export** | [ReportLab](https://www.reportlab.com/) `≥4.1.0` | Generate downloadable PDF reports from research output |
| **Config** | [python-dotenv](https://pypi.org/project/python-dotenv/) `1.2.2` | Environment-based API key management |
| **Runtime** | Python `≥3.12` | Modern Python with `TypedDict`, type annotations |

---

## 📁 Project Structure

```
Research_Assisatant_Agent/
│
├── app/                          # Backend core
│   ├── core/                     # Shared infrastructure
│   │   ├── settings.py           #   Environment config & model selection
│   │   ├── llm.py                #   Shared Gemini LLM instance
│   │   └── logging.py            #   Centralized logger
│   │
│   ├── agents/                   # LLM-powered agent modules
│   │   └── claim_verifier.py     #   Fact-checks claims against source passages
│   │
│   ├── graph/                    # LangGraph orchestration
│   │   ├── state.py              #   ResearchState TypedDict definition
│   │   ├── nodes/                #   Individual workflow nodes
│   │   │   ├── router_node.py    #     Query classification & routing
│   │   │   ├── query_rewrite_node.py   # Search-optimized query rewriting
│   │   │   ├── planner_node.py   #     Task decomposition (Deep)
│   │   │   ├── evidence_node.py  #     Multi-task evidence gathering (Deep)
│   │   │   ├── synthesis_context.py    # Evidence synthesis (Deep)
│   │   │   ├── gap_analysis_node.py    # Quality evaluation & retry logic
│   │   │   ├── claim_splitter_node.py  # Extract verifiable claims
│   │   │   ├── verification_node.py    # Cross-verify claims against sources
│   │   │   ├── report_assembler_node.py # Assemble verified report
│   │   │   ├── search_node.py    #     Web search (Simple)
│   │   │   ├── extract_node.py   #     Page content extraction (Simple)
│   │   │   ├── formatter_node.py #     Content formatting (Simple)
│   │   │   └── answer_node.py    #     Final answer generation (Simple)
│   │   └── workflows/            #   Compiled LangGraph pipelines
│   │       ├── research_router.py    # Top-level router graph
│   │       ├── deep_research.py      # Deep pipeline definition
│   │       └── simple_research.py    # Simple pipeline definition
│   │
│   ├── models/                   # Pydantic data models
│   │   ├── claims.py             #   ClaimResult model
│   │   └── report.py             #   Report structure model
│   │
│   ├── prompts/                  # LLM prompt templates
│   │   └── research_prompt.py    #   Research & synthesis prompts
│   │
│   ├── services/                 # Business logic services
│   │   ├── classifier.py         #   Query complexity classification
│   │   ├── query_rewriter.py     #   Query rewriting logic
│   │   ├── researcher.py         #   Answer generation service
│   │   ├── synthesizer.py        #   Evidence synthesis service
│   │   ├── formatter.py          #   Content formatting service
│   │   ├── document_saver.py     #   Markdown file persistence
│   │   └── report_parser.py      #   Report parsing utilities
│   │
│   ├── tools/                    # External tool integrations
│   │   └── tavily_search.py      #   Tavily Search & Extract wrapper
│   │
│   └── main.py                   # CLI entry point (Rich-based REPL)
│
├── frontend/                     # Streamlit Web GUI
│   ├── state.py                  #   Session state & research history management
│   ├── components/               #   UI components
│   │   ├── sidebar.py            #     Settings, history, and navigation
│   │   ├── report_view.py        #     Report rendering, export, and claims table
│   │   ├── workflow.py           #     Real-time workflow step tracker
│   │   ├── timeline.py           #     Research timeline display
│   │   ├── metrics.py            #     Stats dashboard (sources, time, citations)
│   │   └── sources.py            #     Gathered sources display
│   └── utils/                    #   Frontend utilities
│       ├── styles.py             #     Premium CSS injection
│       ├── callbacks.py          #     LangGraph callback handler for live UI
│       └── pdf_generator.py      #     PDF export logic via ReportLab
│
├── gui.py                        # Streamlit app entry point
├── run.py                        # Shortcut runner
├── data/                         # Saved research reports (Markdown files)
├── pyproject.toml                # Project metadata & dependencies
├── uv.lock                       # Dependency lock file
├── .env.example                  # Environment variable template
├── architecture.md               # Detailed architecture documentation
├── LICENSE                       # MIT License
└── README.md                     # This file
```

---

## ⚡ Quick Start

### Prerequisites

- **Python ≥ 3.12**
- **[uv](https://docs.astral.sh/uv/)** (recommended) or pip
- A **[Google AI API Key](https://aistudio.google.com/app/apikey)** (for Gemini)
- A **[Tavily API Key](https://app.tavily.com/)** (for web search)
- *(Optional)* A **[LangSmith API Key](https://smith.langchain.com/)** for tracing

### 1. Clone the Repository

```bash
git clone https://github.com/Jethva-Parthiv/research-assistant-agent.git
cd research-assistant-agent
```

### 2. Set Up Environment

**Using `uv` (recommended):**

```bash
uv venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

**Using standard Python:**

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

### 3. Install Dependencies

**Using `uv`:**

```bash
uv sync
```

**Using pip:**

```bash
pip install -e .
```

### 4. Configure Environment Variables

Copy the example file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Required for web search
TAVILY_API_KEY=your_tavily_api_key_here

# Optional — LLM model override (defaults to gemini-2.5-flash)
CHAT_MODEL_NAME=gemini-2.5-flash

# Optional — LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=Research_Assistant
```

### 5. Run the Application

#### 🌐 Web GUI (Streamlit)

```bash
# With uv
uv run streamlit run gui.py

# With standard Python
streamlit run gui.py
```

Then open **http://localhost:8501** in your browser.

#### 💻 CLI Interface (Rich Terminal)

```bash
# With uv
uv run python -m app.main

# With standard Python
python -m app.main
```

Type your research query and press Enter. Type `exit`, `quit`, or `bye` to close.

---

## 🔍 Usage Examples

### Example Queries

| Query Type | Example |
|:---|:---|
| **Simple** (auto-routed) | *"What is Retrieval-Augmented Generation?"* |
| **Deep** (auto-routed) | *"Compare transformer architectures: GPT vs BERT vs T5 — strengths, limitations, and best use cases"* |
| **Forced Fast** | Select **Fast Research** mode in the sidebar settings |
| **Forced Deep** | Select **Deep Research** mode in the sidebar settings |

### Web GUI Features

- **🚀 Start Research** — Submits your query through the agentic pipeline
- **⚙️ Advanced Settings** — Choose research mode, max sources, search depth, and LLM temperature
- **📊 Live Metrics** — Track sources found, pages extracted, elapsed time, and citation count in real-time
- **🔗 Gathered Sources** — View all URLs discovered during research
- **⚡ Workflow Steps** — Watch each node transition through `pending → running → completed` live
- **🕒 Timeline** — Chronological log of pipeline events
- **📄 Export PDF / 📝 Export MD** — Download the completed report
- **📋 Copy Report** — One-click copy to clipboard
- **📚 Table of Contents** — Auto-generated from report headings
- **🛡️ Fact-Checking Verdict** — Claims verification table with status badges and confidence scores
- **🗂️ Research History** — Reload or delete past research sessions from the sidebar

---

## 🔄 Pipeline State

The entire workflow shares a central `ResearchState` (defined as a `TypedDict`), enabling each node to read from and write to a shared context:

| Field | Type | Used By |
|:---|:---|:---|
| `query` | `str` | All — original user input |
| `route` | `str` | Router — `"simple"` or `"deep"` |
| `rewritten_query` | `str` | Rewrite → Search |
| `research_tasks` | `List[str]` | Planner → Evidence (Deep) |
| `search_results` | `List[SearchResult]` | Search → Extract (Simple) |
| `extracted_contents` | `List[ExtractedContent]` | Extract → Formatter (Simple) |
| `evidence` | `List[Evidence]` | Evidence → Synthesis (Deep) |
| `synthesis_context` | `str` | Synthesis → Evaluation (Deep) |
| `formatted_context` | `str` | Formatter → Answer (Simple) |
| `final_answer` | `str` | Answer / Synthesis → Output |
| `confidence_scores` | `Dict[str, float]` | Synthesis → Gap Analysis (Deep) |
| `retry_count` | `int` | Controls re-research loop (max 1) |
| `claims` | `List[ClaimResult]` | Claim Splitter → Verification (Deep) |
| `verified_report` | `str` | Report Assembler → Final Output (Deep) |
| `overall_confidence` | `float` | Aggregated verification score |

---

## 🗺️ Roadmap

Planned improvements and future features:

- [ ] PDF / document ingestion for local knowledge
- [ ] Vector database integration for persistent RAG storage
- [ ] Conversational memory across research sessions
- [ ] Multi-agent collaboration patterns
- [ ] Async + streaming responses for faster UI feedback
- [ ] Reranking and retrieval quality evaluation
- [ ] FastAPI backend for API-first deployment
- [ ] Connect sidebar settings (temperature, max sources) to backend

---

## 🎓 Learning Goals

This project explores modern AI engineering concepts:

- **Agentic AI** — Autonomous multi-step task execution
- **LangGraph Workflows** — State machines with conditional routing and retry loops
- **Retrieval-Augmented Generation (RAG)** — Grounded synthesis from live web sources
- **Claim Verification** — Automated fact-checking with confidence scoring
- **AI Orchestration** — Multi-node pipelines with shared state
- **Tool Calling** — LLM-driven web search and content extraction
- **Scalable Agent Architecture** — Modular agents, services, and node separation

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

---

<div align="center">

**Built by [Jethva Parthiv](https://github.com/Jethva-Parthiv)** for learning and research in modern AI engineering and agentic systems.

</div>
