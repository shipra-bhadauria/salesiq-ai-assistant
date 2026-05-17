import streamlit as st
import os
import re
from agent import run_agent

st.set_page_config(page_title="SalesIQ", page_icon="📊", layout="wide")

st.markdown("""
<div style="background:linear-gradient(135deg,#4C6EF5,#7950F2);padding:1.5rem 2rem;border-radius:12px;margin-bottom:1.5rem">
<h1 style="color:white;margin:0">📊 SalesIQ — Sales Intelligence Assistant</h1>
<p style="color:rgba(255,255,255,0.85);margin:0.3rem 0 0 0">Ask me anything about your sales data, trends, team performance, or strategy.</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 💡 Try asking...")
    suggestions = [
        "What is the total revenue and profit?",
        "Who is the top sales rep?",
        "Show me monthly revenue trend",
        "Which product has the highest profit margin?",
        "Show revenue by region as a chart",
        "What are the FY2025 targets?",
        "What risks does the company face?",
        "Who are our top 5 customers?",
    ]
    for s in suggestions:
        if st.button(s, use_container_width=True, key=s):
            st.session_state["prefill"] = s
    st.markdown("---")
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "👋 Hello! I'm **SalesIQ**. Ask me about revenue, profits, charts, or strategy!",
        "chart_path": None
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        cp = msg.get("chart_path")
        if cp and os.path.exists(cp):
            with open(cp, "rb") as f:
                st.image(f.read(), use_container_width=True)

prefill = st.session_state.pop("prefill", None)
user_input = st.chat_input("Ask about sales data, trends, strategy...") or prefill

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "chart_path": None})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = run_agent(user_input)
            response_text = result["output"]
            chart_path = result.get("chart_path")

            # Agent sometimes returns chart as markdown image inside text
            # Extract it and display properly using st.image instead
            if not chart_path:
                match = re.search(r'!\[.*?\]\((assets/.*?\.png)\)', response_text)
                if match:
                    chart_path = match.group(1)
                    response_text = re.sub(r'!\[.*?\]\(assets/.*?\.png\)', '', response_text).strip()

        st.markdown(response_text)
        if chart_path and os.path.exists(chart_path):
            with open(chart_path, "rb") as f:
                st.image(f.read(), use_container_width=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "chart_path": chart_path
    })