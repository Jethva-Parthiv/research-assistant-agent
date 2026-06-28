import streamlit as st

def render_metrics(stats_ph):
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
