import streamlit as st
from frontend.state import get_session_history, load_session

def render_sidebar() -> dict:
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
        
    return {
        "mode": selected_mode,
        "max_sources": max_sources,
        "search_depth": search_depth,
        "temperature": temperature
    }
