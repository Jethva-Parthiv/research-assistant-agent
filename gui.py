import streamlit as st
import time
import logging
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

from app.graph.workflows.research_router import research_router
from app.core.logging import logger

# Import frontend modules
from frontend.state import init_session_state
from frontend.utils.styles import inject_premium_styles
from frontend.utils.callbacks import StreamlitCallbackHandler, StreamlitLogHandler
from frontend.components.sidebar import render_sidebar
from frontend.components.timeline import render_timeline
from frontend.components.metrics import render_metrics
from frontend.components.sources import render_sources
from frontend.components.workflow import render_workflow_steps
from frontend.components.report_view import render_report_view

# Page Config
st.set_page_config(
    page_title="AI Research Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    init_session_state()
    inject_premium_styles()
    
    # Render Sidebar & settings parameters
    settings = render_sidebar()
    
    # Placeholder in sidebar
    st.sidebar.markdown("### 🕒 Timeline")
    timeline_ph = st.sidebar.empty()
    
    # Center Column (Main App Layout) & Right Column (Metrics & Status)
    col_center, col_right = st.columns([7, 3])
    
    # Define Right Column Placeholders globally
    with col_right:
        st.markdown("### 📊 Metrics")
        stats_ph = st.empty()
        st.markdown("### ⚙️ Workflow Steps")
        workflow_ph = st.empty()
        st.markdown("### 🔗 Gathered Sources")
        sources_ph = st.empty()
        
    # Populate Sidebar and Right Column layouts with current state
    render_timeline(timeline_ph)
    render_metrics(stats_ph)
    render_workflow_steps(workflow_ph)
    render_sources(sources_ph)
    
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
            st.session_state.claims = []
            st.session_state.verified_report = None
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
            st.session_state.claims = []
            st.session_state.verified_report = None
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
                
                if settings["mode"] == "Fast Research":
                    input_state["route"] = "simple"
                elif settings["mode"] == "Deep Research":
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
                
                st.session_state.claims = response.get("claims", [])
                st.session_state.verified_report = response.get("verified_report")
                
                if response.get("verified_report"):
                    st.session_state.final_answer = response.get("verified_report")
                else:
                    st.session_state.final_answer = response.get("final_answer", "No answer compiled.")
                
                # Mark any unexecuted pending nodes as skipped
                for k, v in st.session_state.workflow_steps.items():
                    if v == "pending":
                        st.session_state.workflow_steps[k] = "skipped"
                        
            except Exception as err:
                st.error(f"Execution failed: {err}")
                st.session_state.workflow_steps = {k: ("failed" if v == "running" else v) for k, v in st.session_state.workflow_steps.items()}
                
            st.session_state.is_running = False
            logger.removeHandler(log_handler)
            st.rerun()

        # Render report if available
        render_report_view()

if __name__ == "__main__":
    main()
