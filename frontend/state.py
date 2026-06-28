import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import List, Dict

def init_session_state():
    if "query" not in st.session_state:
        st.session_state.query = ""
    if "rewritten_query" not in st.session_state:
        st.session_state.rewritten_query = ""
    if "route_decision" not in st.session_state:
        st.session_state.route_decision = "auto"
    if "workflow_steps" not in st.session_state:
        st.session_state.workflow_steps = {}
    if "planner_tasks" not in st.session_state:
        st.session_state.planner_tasks = []
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    if "extracted_contents" not in st.session_state:
        st.session_state.extracted_contents = []
    if "evidence" not in st.session_state:
        st.session_state.evidence = []
    if "timeline" not in st.session_state:
        st.session_state.timeline = []
    if "stats" not in st.session_state:
        st.session_state.stats = {
            "sources": 0,
            "pages": 0,
            "time": 0.0,
            "citations": 0,
            "mode": "Auto"
        }
    if "final_answer" not in st.session_state:
        st.session_state.final_answer = ""
    if "is_running" not in st.session_state:
        st.session_state.is_running = False

def get_session_history() -> List[Dict]:
    sessions = []
    save_dir = Path("data")
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
        
    for file in save_dir.glob("*.md"):
        try:
            content = file.read_text(encoding="utf-8")
            query = "Untitled Research"
            mode = "Auto"
            elapsed_time = 0.0
            sources_count = 0
            citations_count = 0
            
            if content.startswith("# Metadata"):
                lines = content.split("\n")
                for line in lines:
                    if line.startswith("- **Query**:") or line.startswith("- **query**:"):
                        query = line.split(":", 1)[1].strip()
                    elif line.startswith("- **Mode**:") or line.startswith("- **mode**:"):
                        mode = line.split(":", 1)[1].strip()
                    elif line.startswith("- **Time**:") or line.startswith("- **time**:"):
                        try:
                            elapsed_time = float(line.split(":", 1)[1].replace("s", "").strip())
                        except ValueError:
                            pass
                    elif line.startswith("- **Sources**:") or line.startswith("- **sources**:"):
                        try:
                            sources_count = int(line.split(":", 1)[1].strip())
                        except ValueError:
                            pass
                    elif line.startswith("- **Citations**:") or line.startswith("- **citations**:"):
                        try:
                            citations_count = int(line.split(":", 1)[1].strip())
                        except ValueError:
                            pass
            else:
                for line in content.split("\n"):
                    if line.startswith("# "):
                        query = line[2:].strip()
                        break
                        
            dt = datetime.fromtimestamp(file.stat().st_mtime)
            sessions.append({
                "path": file,
                "query": query,
                "mode": mode,
                "date": dt.strftime("%b %d, %H:%M"),
                "timestamp": file.stat().st_mtime,
                "stats": {
                    "sources": sources_count,
                    "pages": sources_count,
                    "time": elapsed_time,
                    "citations": citations_count,
                    "mode": mode
                }
            })
        except Exception:
            pass
            
    sessions.sort(key=lambda x: x["timestamp"], reverse=True)
    return sessions

def load_session(session: Dict):
    file_path = session["path"]
    content = file_path.read_text(encoding="utf-8")
    main_content = content
    if content.startswith("# Metadata"):
        parts = content.split("\n---\n\n", 1)
        if len(parts) == 2:
            _, main_content = parts
            
    st.session_state.query = session["query"]
    st.session_state.rewritten_query = session["query"]
    st.session_state.route_decision = session["mode"].lower()
    st.session_state.final_answer = main_content
    st.session_state.stats = session["stats"]
    st.session_state.workflow_steps = {
        "router": "completed",
        "query_rewrite_node": "completed",
        "planner_node": "completed" if session["mode"].lower() == "deep" else "pending",
        "search_node": "completed" if session["mode"].lower() == "simple" else "pending",
        "extract_node": "completed" if session["mode"].lower() == "simple" else "pending",
        "formatter_node": "completed" if session["mode"].lower() == "simple" else "pending",
        "answer_node": "completed" if session["mode"].lower() == "simple" else "pending",
        "evidence_node": "completed" if session["mode"].lower() == "deep" else "pending",
        "synthesis_context": "completed" if session["mode"].lower() == "deep" else "pending",
        "gap_analysis_node": "completed" if session["mode"].lower() == "deep" else "pending",
    }
    st.session_state.timeline = [("Loaded", "Loaded historical report.")]
    st.session_state.search_results = []
    st.session_state.planner_tasks = []
