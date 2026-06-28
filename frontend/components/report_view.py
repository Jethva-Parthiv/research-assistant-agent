import re
import streamlit as st
from frontend.utils.pdf_generator import generate_pdf_bytes

def render_report_view():
    if st.session_state.final_answer:
        st.markdown("---")
        
        # Download Actions
        col_act1, col_act2, col_act3, _ = st.columns([3, 3, 3, 3])
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
