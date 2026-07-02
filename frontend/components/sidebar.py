import streamlit as st
from frontend.state import get_session_history, load_session, load_session_from_history

def render_sidebar() -> dict:
    st.sidebar.html("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #2196f3; font-weight: 700; margin-bottom: 0; font-family: 'Inter', sans-serif;">🔬 ResearchFlow</h2>
        <span style="font-size: 11px; color: #757575; font-family: 'Inter', sans-serif;">LangGraph + Gemini Orchestrated</span>
    </div>
    """)
    
    # Session History
    st.sidebar.markdown("### 🗂️ Research History")
    history = st.session_state.get("history", [])
    if history:
        for idx, sess in enumerate(history[:6]):
            col1, col2 = st.sidebar.columns([4, 1])
            with col1:
                disp_query = sess["query"][:28] + "..." if len(sess["query"]) > 28 else sess["query"]
                if st.button(f"{disp_query}\n({sess['date']})", key=f"hist_{idx}", use_container_width=True):
                    load_session_from_history(idx)
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{idx}", use_container_width=True):
                    st.session_state.history.pop(idx)
                    st.rerun()
    else:
        st.sidebar.markdown("<span style='font-size: 12px; color: #757575;'>No saved research found.</span>", unsafe_allow_html=True)
        
    st.sidebar.divider()
    
    selected_mode = st.sidebar.selectbox(
        "Research Mode",
        ["Auto-Detect", "Fast Research", "Deep Research"],
        index=2
    )
        
    return {
        "mode": selected_mode,
        "max_sources": 5,
        "search_depth": "basic",
        "temperature": 0.0
    }
