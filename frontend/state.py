import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from app.models.claims import ClaimResult

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
    if "claims" not in st.session_state:
        st.session_state.claims = []
    if "verified_report" not in st.session_state:
        st.session_state.verified_report = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "state_loaded" not in st.session_state:
        st.session_state.state_loaded = False
        cleanup_old_sessions()
    if "query_input_val" not in st.session_state:
        st.session_state.query_input_val = ""
    if "trigger_search" not in st.session_state:
        st.session_state.trigger_search = False

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
        "claim_splitter": "completed" if session["mode"].lower() == "deep" else "pending",
        "verification": "completed" if session["mode"].lower() == "deep" else "pending",
        "report_assembler": "completed" if session["mode"].lower() == "deep" else "pending",
    }
    st.session_state.timeline = [("Loaded", "Loaded historical report.")]
    st.session_state.search_results = []
    st.session_state.planner_tasks = []

def load_session_from_history(idx: int):
    if 0 <= idx < len(st.session_state.history):
        entry = st.session_state.history[idx]
        st.session_state.query = entry["query"]
        st.session_state.query_input_val = entry["query"]
        st.session_state.rewritten_query = entry["query"]
        st.session_state.route_decision = entry["mode"].lower()
        st.session_state.final_answer = entry["final_answer"]
        st.session_state.verified_report = entry.get("verified_report")
        st.session_state.claims = entry.get("claims", [])
        st.session_state.stats = entry["stats"]
        st.session_state.timeline = entry["timeline"]
        st.session_state.search_results = entry["search_results"]
        st.session_state.workflow_steps = entry["workflow_steps"]

def get_session_file(session_id: str) -> Path:
    save_dir = Path("data/sessions")
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir / f"{session_id}.json"

def save_state_to_file(session_id: str):
    if not session_id:
        return
    import json
    file_path = get_session_file(session_id)
    
    # Serialize claims
    claims_serialized = []
    for c in st.session_state.get("claims", []):
        if isinstance(c, ClaimResult):
            claims_serialized.append(c.model_dump())
        else:
            claims_serialized.append(c)
            
    # Serialize history items
    history_serialized = []
    for entry in st.session_state.get("history", []):
        entry_copy = dict(entry)
        entry_copy["claims"] = [
            c.model_dump() if isinstance(c, ClaimResult) else c 
            for c in entry.get("claims", [])
        ]
        history_serialized.append(entry_copy)
        
    state_data = {
        "query": st.session_state.get("query", ""),
        "rewritten_query": st.session_state.get("rewritten_query", ""),
        "route_decision": st.session_state.get("route_decision", "auto"),
        "final_answer": st.session_state.get("final_answer", ""),
        "verified_report": st.session_state.get("verified_report"),
        "claims": claims_serialized,
        "stats": st.session_state.get("stats", {}),
        "timeline": st.session_state.get("timeline", []),
        "search_results": st.session_state.get("search_results", []),
        "planner_tasks": st.session_state.get("planner_tasks", []),
        "workflow_steps": st.session_state.get("workflow_steps", {}),
        "history": history_serialized
    }
    
    try:
        file_path.write_text(json.dumps(state_data, indent=2), encoding="utf-8")
    except Exception as e:
        import traceback
        traceback.print_exc()

def load_state_from_file(session_id: str) -> bool:
    if not session_id:
        return False
    import json
    file_path = get_session_file(session_id)
    if not file_path.exists():
        return False
        
    try:
        state_data = json.loads(file_path.read_text(encoding="utf-8"))
        
        st.session_state.query = state_data.get("query", "")
        st.session_state.query_input_val = state_data.get("query", "")
        st.session_state.rewritten_query = state_data.get("rewritten_query", "")
        st.session_state.route_decision = state_data.get("route_decision", "auto")
        st.session_state.final_answer = state_data.get("final_answer", "")
        st.session_state.verified_report = state_data.get("verified_report")
        
        # Deserialize claims
        st.session_state.claims = [
            ClaimResult(**c) for c in state_data.get("claims", [])
        ]
        
        st.session_state.stats = state_data.get("stats", {})
        st.session_state.timeline = state_data.get("timeline", [])
        st.session_state.search_results = state_data.get("search_results", [])
        st.session_state.planner_tasks = state_data.get("planner_tasks", [])
        st.session_state.workflow_steps = state_data.get("workflow_steps", {})
        
        # Deserialize history
        history_deserialized = []
        for entry in state_data.get("history", []):
            entry_copy = dict(entry)
            entry_copy["claims"] = [
                ClaimResult(**c) for c in entry.get("claims", [])
            ]
            history_deserialized.append(entry_copy)
        st.session_state.history = history_deserialized
        st.session_state.state_loaded = True
        
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False

def cleanup_old_sessions():
    save_dir = Path("data/sessions")
    if not save_dir.exists():
        return
    import time
    now = time.time()
    for file in save_dir.glob("*.json"):
        # If older than 24 hours (86400 seconds)
        if now - file.stat().st_mtime > 86400:
            try:
                file.unlink()
            except Exception:
                pass
