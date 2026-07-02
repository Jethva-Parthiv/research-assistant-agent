import re
import streamlit as st
from frontend.utils.pdf_generator import generate_pdf_bytes

def render_report_view():
    if st.session_state.final_answer:
        st.markdown("---")
        
        # Download Actions
        col_act1, col_act2, _ = st.columns([3, 3, 6])
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
                
        st.markdown("## 🔍 Compiled Report")
        
        # Determine target text to search for headings (use verified_report if available)
        report_to_render = st.session_state.get("verified_report") or st.session_state.final_answer
        
        with st.expander("📚 Table of Contents", expanded=False):
            headings = re.findall(r'^#+\s+(.+)$', report_to_render, re.MULTILINE)
            for h in headings:
                # Strip HTML tags from heading in Table of Contents to look clean
                h_clean = re.sub(r'<[^>]*>', '', h)
                st.markdown(f"- {h_clean}")
                
        st.markdown(report_to_render, unsafe_allow_html=True)
        
        # Display Claims Verification Details below the report if claims exist
        claims = st.session_state.get("claims") or []
        if claims:
            st.markdown("---")
            st.markdown("### 🛡️ Fact-Checking & Verification Verdict")
            
            total_claims = len(claims)
            verified_count = sum(1 for c in claims if c.status == "verified")
            weak_count = sum(1 for c in claims if c.status == "weak")
            unverified_count = sum(1 for c in claims if c.status == "unverified")
            conflicted_count = sum(1 for c in claims if c.status == "conflicted")
            other_unverified = unverified_count + conflicted_count
            
            # 1. Summary Metrics Bar
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric(label="Claims Extracted", value=total_claims)
            with col_m2:
                # Color code green for high verification ratio
                v_ratio = verified_count / total_claims if total_claims else 0.0
                st.metric(
                    label="Verified Claims", 
                    value=f"{verified_count} / {total_claims}", 
                    delta=f"{v_ratio*100:.1f}% Verified" if total_claims else None,
                    delta_color="normal" if v_ratio >= 0.5 else "inverse"
                )
            with col_m3:
                st.metric(label="Weak Support", value=weak_count)
            with col_m4:
                st.metric(label="Unverified / Conflicted", value=other_unverified)
                
            # Progress bar depicting verified ratio
            if total_claims:
                st.progress(
                    verified_count / total_claims, 
                    text=f"Integrity Score: {verified_count} of {total_claims} claims verified ({v_ratio*100:.1f}%)"
                )
                
            # 2. Expandable Claim Verification Details with a colored HTML Table
            with st.expander("🔬 Claim Verification Details", expanded=False):
                table_html = """
                <table style="width:100%; border-collapse: collapse; font-family: 'Inter', sans-serif; font-size: 14px; margin-top: 8px;">
                    <thead>
                        <tr style="background-color: #1e1e1e; border-bottom: 2px solid #444444;">
                            <th style="padding: 12px 10px; text-align: left; font-weight: 600; color: #ffffff;">Claim</th>
                            <th style="padding: 12px 10px; text-align: left; font-weight: 600; color: #ffffff; width: 140px;">Status</th>
                            <th style="padding: 12px 10px; text-align: left; font-weight: 600; color: #ffffff; width: 100px;">Confidence</th>
                            <th style="padding: 12px 10px; text-align: left; font-weight: 600; color: #ffffff; width: 140px;">Source</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                for c in claims:
                    # Select colors: green for verified, yellow/amber for weak, red for unverified/conflicted
                    status_text = c.status.upper()
                    if c.status == "verified":
                        bg_color = "rgba(46, 125, 50, 0.15)"
                        text_color = "#81c784"
                    elif c.status == "weak":
                        bg_color = "rgba(245, 127, 23, 0.15)"
                        text_color = "#fff176"
                    else:  # unverified or conflicted
                        bg_color = "rgba(198, 40, 40, 0.15)"
                        text_color = "#e57373"
                        
                    source_link = f'<a href="{c.source_url}" target="_blank" style="color: #64b5f6; text-decoration: none; font-weight: 500;">✓ View Source</a>' if c.source_url else '<span style="color: #888888; font-style: italic;">No URL</span>'
                    
                    table_html += f"""
                        <tr style="border-bottom: 1px solid #333333;">
                            <td style="padding: 12px 10px; color: #e0e0e0; line-height: 1.5;">{c.claim_text}</td>
                            <td style="padding: 12px 10px; font-weight: 600;"><span style="background-color: {bg_color}; color: {text_color}; padding: 4px 10px; border-radius: 4px; display: inline-block; font-size: 0.85em; border: 1px solid {text_color}60;">{status_text}</span></td>
                            <td style="padding: 12px 10px; color: #e0e0e0; font-weight: 500;">{c.confidence:.2f}</td>
                            <td style="padding: 12px 10px;">{source_link}</td>
                        </tr>
                    """
                    
                table_html += """
                    </tbody>
                </table>
                """
                
                st.html(table_html)
