import time
import re
import logging
from datetime import datetime
import streamlit as st
from langchain_core.callbacks import BaseCallbackHandler
from app.core.logging import logger

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
        
    @property
    def has_session_state(self) -> bool:
        try:
            return "workflow_steps" in st.session_state
        except Exception:
            return False
            
    def add_event(self, text: str):
        if not self.has_session_state:
            return
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
                ("synthesis_context", "Synthesis Context", "Synthesize findings into structured report"),
                ("claim_splitter", "Claim Splitter", "Deconstruct report into atomic claims"),
                ("verification", "Verification Node", "Verify claims against extracted source passages"),
                ("report_assembler", "Report Assembler", "Compile verified report with status badges")
            ]
            if st.session_state.workflow_steps.get("gap_analysis_node") in ["running", "completed", "failed"]:
                steps.insert(5, ("gap_analysis_node", "Gap Analysis Node", "Identify report gaps and generate new queries"))
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
        if not self.has_session_state:
            return
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
        if not self.has_session_state:
            return
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
        if not self.has_session_state:
            return
        run_id = kwargs.get("run_id")
        node_name = self.run_to_node.get(run_id)
        
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
