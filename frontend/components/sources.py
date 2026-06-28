import streamlit as st

def render_sources(sources_ph):
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
