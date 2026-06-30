import streamlit as st

def render_workflow_steps(workflow_ph):
    steps = []
    if st.session_state.route_decision == "deep":
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
