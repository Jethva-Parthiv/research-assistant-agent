import streamlit as st

def inject_premium_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .spin-indicator {
        border: 2px solid rgba(255,255,255,0.2);
        border-left-color: #ff9800;
        border-radius: 50%;
        width: 14px;
        height: 14px;
        animation: spin 1s linear infinite;
        display: inline-block;
    }
    .pulse-card {
        animation: pulse 2s infinite ease-in-out;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .stat-metric {
        font-size: 24px;
        font-weight: 700;
        color: #2196f3;
    }
    </style>
    """, unsafe_allow_html=True)
