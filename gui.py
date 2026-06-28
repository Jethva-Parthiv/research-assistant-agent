import streamlit as st
import time
import os
import io
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

from langchain_core.callbacks import BaseCallbackHandler
from app.graph.workflows.research_router import research_router
from app.services.document_saver import save_document
from app.core.logging import logger
import logging

# ---------------------------------------------------------
# Page Configurations & CSS
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Research Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Typography, Styling and Animations
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
@keyframes pulse {
    0% { opacity: 0.6; }
    50% { opacity: 1; }
    100% { opacity: 0.6; }
}
.spin-indicator {
    border: 2px solid rgba(255,255,255,0.2);
    border-left-color: #ff9800;
    border-radius: 50%;
    width: 14px;
    height: 14px;
    animation: spin 1s linear infinite;
    display: inline-block;
}
.pulse-card {
    animation: pulse 2s infinite ease-in-out;
}
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
}
.stat-metric {
    font-size: 24px;
    font-weight: 700;
    color: #2196f3;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PDF Export Helper (using ReportLab)
# ---------------------------------------------------------
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_bytes(markdown_text: str) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1976d2'),
        spaceAfter=15
    )
    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#1e88e5'),
        spaceBefore=14,
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#42a5f5'),
        spaceBefore=10,
        spaceAfter=5
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#212121'),
        spaceAfter=8
    )
    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )
    
    story = []
    in_code_block = False
    
    # Strip markdown specific syntax
    lines = markdown_text.split('\n')
    for line in lines:
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 4))
            continue
            
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            continue
            
        if in_code_block:
            story.append(Paragraph(f"<code>{stripped}</code>", body_style))
            continue
            
        if stripped.startswith('# '):
            story.append(Paragraph(stripped[2:], title_style))
        elif stripped.startswith('## '):
            story.append(Paragraph(stripped[3:], h1_style))
        elif stripped.startswith('### '):
            story.append(Paragraph(stripped[4:], h2_style))
        elif stripped.startswith('* ') or stripped.startswith('- '):
            story.append(Paragraph(f"&bull; {stripped[2:]}", bullet_style))
        else:
            # Simple clean up of raw inline markdown formatting tags
            cleaned = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', stripped)
            cleaned = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', cleaned)
            story.append(Paragraph(cleaned, body_style))
            
    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data

# ---------------------------------------------------------
# Session & History Management
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# Dynamic Callback Handler & Log Handler
# ---------------------------------------------------------
class StreamlitCallbackHandler(BaseCallbackHandler):
    def __init__(self, workflow_ph, timeline_ph, sources_ph, stats_ph, rewrite_ph, plan_ph, status_ph):
        self.workflow_ph = workflow_ph
        self.timeline_ph = timeline_ph
        self.sources_ph = sources_ph
        self.stats_ph = stats_ph
        self.rewrite_ph = rewrite_ph
        self.plan_ph = plan_ph
        self.status_ph = status_ph
        self.run_to_node = {}
        self.start_time = time.time()
        self.mode = "simple"
        
    def add_event(self, text: str):
        now = datetime.now().strftime("%H:%M:%S")
        st.session_state.timeline.append((now, text))
        self.render_timeline()

    def update_workflow(self, active_node: str):
        html = f'<div style="font-family: \'Inter\', sans-serif;">'
        if self.mode == "deep":
            steps = [
                ("router", "Route Decision", "Classify query complexity"),
                ("query_rewrite_node", "Query Rewrite", "Optimize query terms for web search"),
                ("planner_node", "Planner Node", "Decompose query into sub-tasks"),
                ("evidence_node", "Evidence Node", "Concurrently gather search evidence"),
                ("synthesis_context", "Synthesis Context", "Synthesize findings into structured report")
            ]
            if st.session_state.workflow_steps.get("gap_analysis_node") in ["running", "completed", "failed"]:
                steps.append(("gap_analysis_node", "Gap Analysis Node", "Identify report gaps and generate new queries"))
        else:
            steps = [
                ("router", "Route Decision", "Classify query complexity"),
                ("query_rewrite_node", "Query Rewrite", "Optimize query terms for web search"),
                ("search_node", "Search Node", "Query Tavily for top websites"),
                ("extract_node", "Extract Node", "Scrape text content from URLs"),
                ("formatter_node", "Formatter Node", "Prepare context for generation"),
                ("answer_node", "Answer Node", "Generate structured response with citations")
            ]
            
        for node_id, label, desc in steps:
            state = st.session_state.workflow_steps.get(node_id, "pending")
            
            if state == "completed":
                icon = "✓"
                color = "#2e7d32"
                icon_style = "background-color: #2e7d32; color: white;"
            elif state == "skipped":
                icon = "―"
                color = "#757575"
                icon_style = "background-color: #e0e0e0; color: #757575; border: 1px solid #bdbdbd;"
                desc = desc + " (Skipped)"
            elif state == "running":
                icon = ""
                color = "#ff9800"
                icon_style = "border: 2px solid rgba(0,0,0,0.1); border-left-color: #ff9800; border-radius: 50%; width: 14px; height: 14px; animation: spin 1s linear infinite;"
            elif state == "failed":
                icon = "✗"
                color = "#d32f2f"
                icon_style = "background-color: #d32f2f; color: white;"
            else:
                icon = "○"
                color = "#757575"
                icon_style = "border: 2px solid #bdbdbd; color: #757575; background: transparent;"
                
            is_active = (node_id == active_node)
            border_style = "border-left: 2px solid #2196f3;" if is_active else "border-left: 2px solid #e0e0e0;"
            
            html += f"""
            <div style="padding-left: 12px; margin-bottom: 16px; {border_style} margin-left: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="display: flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; font-size: 11px; font-weight: bold; {icon_style}">
                        {icon}
                    </div>
                    <div>
                        <strong style="color: {color}; font-size: 13px;">{label}</strong><br/>
                        <span style="font-size: 11px; color: #757575;">{desc}</span>
                    </div>
                </div>
            </div>
            """
        html += '</div>'
        self.workflow_ph.html(html)

    def render_timeline(self):
        html = '<div style="font-family: \'Inter\', sans-serif;">'
        for tm, msg in st.session_state.timeline[-10:]:
            html += f"""
            <div style="margin-bottom: 8px; font-size: 12px;">
                <span style="color: #2196f3; font-weight: 500; margin-right: 6px;">{tm}</span>
                <span style="color: #bdbdbd;">{msg}</span>
            </div>
            """
        html += '</div>'
        self.timeline_ph.html(html)

    def render_stats(self, sources_found=0, pages_extracted=0, citations=0):
        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)
        time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
        
        st.session_state.stats = {
            "sources": sources_found,
            "pages": pages_extracted,
            "time": elapsed,
            "citations": citations,
            "mode": self.mode.upper()
        }
        
        html = f"""
        <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; font-family: 'Inter', sans-serif;">
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 11px; color: #757575;">Sources Found</div>
                <div class="stat-metric">{sources_found}</div>
            </div>
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 11px; color: #757575;">Citations</div>
                <div class="stat-metric">{citations}</div>
            </div>
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 11px; color: #757575;">Search Mode</div>
                <div style="font-size: 14px; font-weight: bold; color: #ff9800; margin-top: 6px;">{self.mode.upper()}</div>
            </div>
            <div class="glass-card" style="text-align: center;">
                <div style="font-size: 11px; color: #757575;">Elapsed Time</div>
                <div style="font-size: 14px; font-weight: bold; color: #2e7d32; margin-top: 6px;">{time_str}</div>
            </div>
        </div>
        """
        self.stats_ph.html(html)

    def render_sources(self):
        html = '<div style="font-family: \'Inter\', sans-serif; max-height: 250px; overflow-y: auto;">'
        sources = st.session_state.get("search_results", [])
        if not sources:
            html += '<div style="font-size: 12px; color: #757575; text-align: center;">No sources gathered yet.</div>'
        else:
            for idx, src in enumerate(sources, start=1):
                title = src.get("title", "Source Page")
                url = src.get("url", "")
                domain = url.split("//")[-1].split("/")[0] if url else "web"
                html += f"""
                <div class="glass-card" style="padding: 10px; margin-bottom: 8px; border-left: 3px solid #2196f3;">
                    <div style="font-size: 12px; font-weight: 500; color: #e0e0e0; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">[{idx}] {title}</div>
                    <div style="font-size: 10px; color: #757575;">{domain}</div>
                    <a href="{url}" target="_blank" style="font-size: 10px; color: #2196f3; text-decoration: none;">View Source ↗</a>
                </div>
                """
        html += '</div>'
        self.sources_ph.html(html)

    def refresh_ui(self, active_node=""):
        self.update_workflow(active_node)
        self.render_sources()
        
        # Calculate stats
        results = st.session_state.get("search_results", [])
        pages = len(st.session_state.get("extracted_contents", []))
        citations = 0
        if st.session_state.final_answer:
            citations = len(re.findall(r'\[\d+\]', st.session_state.final_answer))
            
        self.render_stats(len(results), pages, citations)

    def on_chain_start(self, serialized, prompts, **kwargs):
        run_id = kwargs.get("run_id")
        metadata = kwargs.get("metadata", {})
        node_name = metadata.get("langgraph_node")
        
        if node_name:
            self.run_to_node[run_id] = node_name
            st.session_state.workflow_steps[node_name] = "running"
            
            # Specific node event logging
            if node_name == "router":
                self.add_event("Classifying query route...")
            elif node_name == "query_rewrite_node":
                self.add_event("Rewriting search query...")
            elif node_name == "planner_node":
                self.add_event("Generating task research checklist...")
            elif node_name == "search_node":
                self.add_event("Querying Tavily Web Index...")
            elif node_name == "extract_node":
                self.add_event("Scraping and extracting full webpage contents...")
            elif node_name == "evidence_node":
                self.add_event("Running parallel evidence searches...")
            elif node_name == "formatter_node":
                self.add_event("Formatting references for answer builder...")
            elif node_name in ["answer_node", "synthesis_context"]:
                self.add_event("Synthesizing citations and compiling final report...")
            elif node_name == "gap_analysis_node":
                self.add_event("Self-evaluation score < 3.5. Executing gap analysis...")
                
            self.refresh_ui(node_name)

    def on_chain_end(self, outputs, **kwargs):
        run_id = kwargs.get("run_id")
        node_name = self.run_to_node.get(run_id)
        
        # Safely ignore inner chain runs with string/non-dict outputs to prevent AttributeError
        if not isinstance(outputs, dict):
            return
            
        if node_name:
            st.session_state.workflow_steps[node_name] = "completed"
            
            if node_name == "router":
                route = outputs.get("route", "simple").strip().lower()
                self.mode = "deep" if route == "deep" else "simple"
                st.session_state.route_decision = self.mode
                self.add_event(f"Route selected: **{self.mode.upper()}**")
                
            elif node_name == "query_rewrite_node":
                rewritten = outputs.get("rewritten_query", "")
                st.session_state.rewritten_query = rewritten
                self.rewrite_ph.html(f"""
                <div class="glass-card" style="border-left: 4px solid #ff9800; font-size: 13px;">
                    <div style="color: #757575; font-size: 10px; text-transform: uppercase; font-weight: bold; margin-bottom: 4px;">Optimized Search Terms</div>
                    <span style="color: #e0e0e0; font-style: italic;">"{rewritten}"</span>
                </div>
                """)
                self.add_event("Search terms optimized successfully.")
                
            elif node_name == "planner_node":
                tasks = outputs.get("research_tasks", [])
                st.session_state.planner_tasks = tasks
                task_html = '<div class="glass-card" style="font-size: 13px;"><div style="color:#757575; font-size:10px; text-transform:uppercase; font-weight:bold; margin-bottom:6px;">Checklist Plan</div>'
                for t in tasks:
                    task_html += f'<div style="margin-bottom:4px; color:#bdbdbd;">✓ {t}</div>'
                task_html += '</div>'
                self.plan_ph.html(task_html)
                self.add_event(f"Checklist built with {len(tasks)} sub-tasks.")
                
            elif node_name == "search_node":
                results = outputs.get("search_results", [])
                st.session_state.search_results = results
                self.add_event(f"Retrieved {len(results)} search sources.")
                
            elif node_name == "extract_node":
                contents = outputs.get("extracted_contents", [])
                st.session_state.extracted_contents = contents
                self.add_event(f"Extracted content from {len(contents)} target domains.")
                
            elif node_name == "evidence_node":
                evidence = outputs.get("evidence", [])
                st.session_state.evidence = evidence
                # Tavily results are nested in evidence for deep workflow
                results = [{"title": e.get("task", "Evidence"), "url": e.get("source", ""), "content": e.get("content", "")} for e in evidence if e.get("source")]
                st.session_state.search_results = results
                self.add_event(f"Concurrently compiled {len(evidence)} evidence points.")
                
            elif node_name in ["answer_node", "synthesis_context"]:
                ans = outputs.get("final_answer", "")
                st.session_state.final_answer = ans
                self.add_event("Report synthesis complete.")
                
            self.refresh_ui(node_name)

class StreamlitLogHandler(logging.Handler):
    def __init__(self, status_ph):
        super().__init__()
        self.status_ph = status_ph

    def emit(self, record):
        try:
            log_msg = self.format(record)
            if "Searching:" in log_msg:
                self.status_ph.info(f"🔎 {log_msg}")
            elif "Extracting" in log_msg:
                self.status_ph.info(f"📄 {log_msg}")
            elif "saved" in log_msg:
                self.status_ph.success(f"💾 {log_msg}")
            else:
                self.status_ph.info(f"⚙️ {log_msg}")
        except Exception:
            pass

# ---------------------------------------------------------
# UI Components & Layout
# ---------------------------------------------------------
def main():
    init_session_state()
    
    # ----------------------------------
    # Sidebar - Left Panel & Settings
    # ----------------------------------
    st.sidebar.html("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #2196f3; font-weight: 700; margin-bottom: 0; font-family: 'Inter', sans-serif;">RESEARCH AGENT</h2>
        <span style="font-size: 11px; color: #757575; font-family: 'Inter', sans-serif;">LangGraph + Gemini Orchestrated</span>
    </div>
    """)
    
    # Session History
    st.sidebar.markdown("### 🗂️ Research History")
    history = get_session_history()
    if history:
        for idx, sess in enumerate(history[:6]):
            col1, col2 = st.sidebar.columns([4, 1])
            with col1:
                disp_query = sess["query"][:28] + "..." if len(sess["query"]) > 28 else sess["query"]
                if st.button(f"{disp_query}\n({sess['date']})", key=f"hist_{idx}", use_container_width=True):
                    load_session(sess)
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                    try:
                        sess["path"].unlink()
                        st.rerun()
                    except Exception:
                        pass
    else:
        st.sidebar.markdown("<span style='font-size: 12px; color: #757575;'>No saved research found.</span>", unsafe_allow_html=True)
        
    st.sidebar.divider()
    
    # Collapsible Settings
    with st.sidebar.expander("🛠️ Advanced Settings", expanded=False):
        selected_mode = st.selectbox(
            "Research Mode",
            ["Auto-Detect", "Fast Research", "Deep Research"],
            index=0
        )
        max_sources = st.slider("Max Sources", min_value=3, max_value=20, value=5)
        search_depth = st.selectbox("Search Depth", ["basic", "advanced"], index=0)
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
    
    auto_save = True
        
    st.sidebar.markdown("### 🕒 Timeline")
    timeline_ph = st.sidebar.empty()
    
    # ----------------------------------
    # Center Column (Main App Layout)
    # ----------------------------------
    col_center, col_right = st.columns([7, 3])
    
    # Define Right Column Placeholders globally
    with col_right:
        st.markdown("### 📊 Metrics")
        stats_ph = st.empty()
        st.markdown("### ⚙️ Workflow Steps")
        workflow_ph = st.empty()
        st.markdown("### 🔗 Gathered Sources")
        sources_ph = st.empty()

    # Populate Metrics Placeholder with current state
    elapsed = st.session_state.stats.get('time', 0.0)
    mins, secs = divmod(int(elapsed), 60)
    time_str = f"{mins}m {secs}s" if mins > 0 else f"{secs}s"
    stats_html = f"""
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; font-family: 'Inter', sans-serif;">
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 11px; color: #757575;">Sources Found</div>
            <div class="stat-metric">{st.session_state.stats.get('sources', 0)}</div>
        </div>
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 11px; color: #757575;">Citations</div>
            <div class="stat-metric">{st.session_state.stats.get('citations', 0)}</div>
        </div>
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 11px; color: #757575;">Search Mode</div>
            <div style="font-size: 14px; font-weight: bold; color: #ff9800; margin-top: 6px;">{st.session_state.stats.get('mode', 'Auto')}</div>
        </div>
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 11px; color: #757575;">Research Time</div>
            <div style="font-size: 14px; font-weight: bold; color: #2e7d32; margin-top: 6px;">{time_str}</div>
        </div>
    </div>
    """
    stats_ph.html(stats_html)

    # Populate Workflow Steps Placeholder with current state
    steps = []
    if st.session_state.route_decision == "deep":
        steps = [
            ("router", "Route Decision", "Classify query complexity"),
            ("query_rewrite_node", "Query Rewrite", "Optimize query terms for web search"),
            ("planner_node", "Planner Node", "Decompose query into sub-tasks"),
            ("evidence_node", "Evidence Node", "Concurrently gather search evidence"),
            ("synthesis_context", "Synthesis Context", "Synthesize findings into structured report")
        ]
        if st.session_state.workflow_steps.get("gap_analysis_node") in ["running", "completed", "failed"]:
            steps.append(("gap_analysis_node", "Gap Analysis Node", "Identify report gaps and generate new queries"))
    elif st.session_state.route_decision == "simple":
        steps = [
            ("router", "Route Decision", "Classify query complexity"),
            ("query_rewrite_node", "Query Rewrite", "Optimize query terms for web search"),
            ("search_node", "Search Node", "Query Tavily for top websites"),
            ("extract_node", "Extract Node", "Scrape text content from URLs"),
            ("formatter_node", "Formatter Node", "Prepare context for generation"),
            ("answer_node", "Answer Node", "Generate structured response with citations")
        ]
    if steps:
        workflow_html = f'<div style="font-family: \'Inter\', sans-serif;">'
        for node_id, label, desc in steps:
            state = st.session_state.workflow_steps.get(node_id, "pending")
            if state == "completed":
                icon, color, icon_style = "✓", "#2e7d32", "background-color: #2e7d32; color: white;"
            elif state == "skipped":
                icon, color, icon_style = "―", "#757575", "background-color: #e0e0e0; color: #757575; border: 1px solid #bdbdbd;"
                desc = desc + " (Skipped)"
            elif state == "failed":
                icon, color, icon_style = "✗", "#d32f2f", "background-color: #d32f2f; color: white;"
            elif state == "running":
                icon, color, icon_style = "", "#ff9800", "border: 2px solid rgba(0,0,0,0.1); border-left-color: #ff9800; border-radius: 50%; width: 14px; height: 14px; animation: spin 1s linear infinite;"
            else:
                icon, color, icon_style = "○", "#757575", "border: 2px solid #bdbdbd; color: #757575; background: transparent;"
                
            workflow_html += f"""
            <div style="padding-left: 12px; margin-bottom: 16px; border-left: 2px solid #e0e0e0; margin-left: 8px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="display: flex; align-items: center; justify-content: center; width: 20px; height: 20px; border-radius: 50%; font-size: 11px; font-weight: bold; {icon_style}">
                        {icon}
                    </div>
                    <div>
                        <strong style="color: {color}; font-size: 13px;">{label}</strong><br/>
                        <span style="font-size: 11px; color: #757575;">{desc}</span>
                    </div>
                </div>
            </div>
            """
        workflow_html += '</div>'
        workflow_ph.html(workflow_html)

    # Populate Sources Placeholder with current state
    sources_html = '<div style="font-family: \'Inter\', sans-serif; max-height: 300px; overflow-y: auto;">'
    sources = st.session_state.get("search_results", [])
    if not sources:
        sources_html += '<div style="font-size: 12px; color: #757575; text-align: center;">No sources gathered yet.</div>'
    else:
        for idx, src in enumerate(sources, start=1):
            title = src.get("title", "Source Page")
            url = src.get("url", "")
            domain = url.split("//")[-1].split("/")[0] if url else "web"
            sources_html += f"""
            <div class="glass-card" style="padding: 10px; margin-bottom: 8px; border-left: 3px solid #2196f3;">
                <div style="font-size: 12px; font-weight: 500; color: #e0e0e0; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">[{idx}] {title}</div>
                <div style="font-size: 10px; color: #757575;">{domain}</div>
                <a href="{url}" target="_blank" style="font-size: 10px; color: #2196f3; text-decoration: none;">View Source ↗</a>
            </div>
            """
    sources_html += '</div>'
    sources_ph.html(sources_html)

    # Populate Timeline (sidebar)
    if st.session_state.timeline:
        timeline_html = '<div style="font-family: \'Inter\', sans-serif;">'
        for tm, msg in st.session_state.timeline[-10:]:
            timeline_html += f"""
            <div style="margin-bottom: 8px; font-size: 12px;">
                <span style="color: #2196f3; font-weight: 500; margin-right: 6px;">{tm}</span>
                <span style="color: #757575;">{msg}</span>
            </div>
            """
        timeline_html += '</div>'
        timeline_ph.html(timeline_html)

    # Center Column Content Rendering
    with col_center:
        st.html("<h1 style='color: #2196f3; font-weight: 700; margin-bottom: 0px; font-family: \"Inter\", sans-serif;'>Research Hub</h1>")
        st.html("<p style='color: #757575; font-size: 13px; font-family: \"Inter\", sans-serif;'>Conduct grounded deep research with automated source extraction & citation validation.</p>")
        
        # Search Box
        query_input = st.text_input(
            "What do you want to research today?",
            placeholder="Ask anything (e.g., Explain the details of Retrieval-Augmented Generation)...",
            value=st.session_state.query,
            label_visibility="collapsed"
        )
        
        col_btn1, col_btn2, col_btn3 = st.columns([2.5, 2.5, 7])
        with col_btn1:
            search_clicked = st.button("🚀 Start Research", use_container_width=True)
        with col_btn2:
            clear_clicked = st.button("🧹 Clear", use_container_width=True)
            
        if clear_clicked:
            st.session_state.query = ""
            st.session_state.final_answer = ""
            st.session_state.rewritten_query = ""
            st.session_state.search_results = []
            st.session_state.planner_tasks = []
            st.session_state.timeline = []
            st.session_state.stats = {
                "sources": 0,
                "pages": 0,
                "time": 0.0,
                "citations": 0,
                "mode": "Auto"
            }
            st.session_state.workflow_steps = {}
            st.rerun()

        # Placeholders for intermediate outputs in the center
        rewrite_ph = st.empty()
        plan_ph = st.empty()
        status_ph = st.empty()
        
        # Register logs handler
        log_handler = StreamlitLogHandler(status_ph)
        logger.addHandler(log_handler)
        logger.setLevel(logging.INFO)
        
        # If running
        if search_clicked and query_input:
            st.session_state.query = query_input
            st.session_state.final_answer = ""
            st.session_state.timeline = []
            st.session_state.search_results = []
            st.session_state.planner_tasks = []
            st.session_state.workflow_steps = {
                "router": "pending",
                "query_rewrite_node": "pending",
                "planner_node": "pending",
                "search_node": "pending",
                "extract_node": "pending",
                "formatter_node": "pending",
                "answer_node": "pending",
                "evidence_node": "pending",
                "synthesis_context": "pending",
                "gap_analysis_node": "pending",
            }
            
            st.session_state.is_running = True
            
            # Setup handler using globally defined placeholders
            handler = StreamlitCallbackHandler(
                workflow_ph=workflow_ph,
                timeline_ph=timeline_ph,
                sources_ph=sources_ph,
                stats_ph=stats_ph,
                rewrite_ph=rewrite_ph,
                plan_ph=plan_ph,
                status_ph=status_ph
            )
            
            # Run Graph
            try:
                input_state = {"query": query_input}
                
                if selected_mode == "Fast Research":
                    input_state["route"] = "simple"
                elif selected_mode == "Deep Research":
                    input_state["route"] = "deep"
                    
                from streamlit.runtime.scriptrunner import get_script_run_ctx
                ctx = get_script_run_ctx()
                
                response = research_router.invoke(
                    input_state,
                    config={
                        "callbacks": [handler],
                        "configurable": {
                            "script_run_ctx": ctx
                        }
                    }
                )
                
                st.session_state.final_answer = response.get("final_answer", "No answer compiled.")
                
                # Mark any unexecuted pending nodes as skipped
                for k, v in st.session_state.workflow_steps.items():
                    if v == "pending":
                        st.session_state.workflow_steps[k] = "skipped"
                
                # Auto save
                if auto_save:
                    elapsed = time.time() - handler.start_time
                    save_document(
                        st.session_state.final_answer,
                        metadata={
                            "Query": query_input,
                            "Mode": handler.mode.upper(),
                            "Time": f"{elapsed:.2f}s",
                            "Sources": len(st.session_state.search_results),
                            "Citations": len(re.findall(r'\[\d+\]', st.session_state.final_answer))
                        }
                    )
                    handler.add_event("Report saved successfully to data index.")
                    
            except Exception as err:
                st.error(f"Execution failed: {err}")
                st.session_state.workflow_steps = {k: ("failed" if v == "running" else v) for k, v in st.session_state.workflow_steps.items()}
                
            st.session_state.is_running = False
            logger.removeHandler(log_handler)
            st.rerun()

        # Render report if available
        if st.session_state.final_answer:
            st.markdown("---")
            
            # Download Actions
            col_act1, col_act2, col_act3, col_act4 = st.columns([3, 3, 3, 3])
            with col_act1:
                st.download_button(
                    label="📄 Export PDF",
                    data=generate_pdf_bytes(st.session_state.final_answer),
                    file_name="research_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            with col_act2:
                st.download_button(
                    label="📝 Export MD",
                    data=st.session_state.final_answer,
                    file_name="research_report.md",
                    mime="text/plain",
                    use_container_width=True
                )
            with col_act3:
                if st.button("📋 Copy Report", use_container_width=True):
                    st.components.v1.html(f"""
                    <textarea id="reportText" style="display:none;">{st.session_state.final_answer}</textarea>
                    <script>
                    navigator.clipboard.writeText(document.getElementById('reportText').value);
                    alert('Copied report to clipboard!');
                    </script>
                    """, height=0)
                    
            st.markdown("## 🔍 Compiled Report")
            
            with st.expander("📚 Table of Contents", expanded=False):
                headings = re.findall(r'^#+\s+(.+)$', st.session_state.final_answer, re.MULTILINE)
                for h in headings:
                    st.markdown(f"- {h}")
                    
            st.markdown(st.session_state.final_answer)

if __name__ == "__main__":
    main()
