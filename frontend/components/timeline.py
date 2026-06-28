import streamlit as st

def render_timeline(timeline_ph):
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
