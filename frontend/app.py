import requests
import streamlit as st

# 1. Custom CSS Injection (The "Beauty" Layer)
st.set_page_config(page_title="Buss Intelligence Engine", page_icon="🚌", layout="wide")

st.markdown(f"""
    <style>
    /* Global Background */
    .stApp {{
        background-color: #f8f9fa;
    }}

    /* Header: Dark Grey */
    .main-header {{
        background-color: #333333;
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}

    /* Submit Button: Green */
    div.stButton > button {{
        background-color: #008a4f;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }}
    div.stButton > button:hover {{
        background-color: #006b3d;
        color: white;
        border: none;
        transform: translateY(-1px);
    }}
    div.stButton > button:active {{
        background-color: #008a4f;
        color: white;
    }}

    /* Card Styling */
    .data-card {{
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #008a4f;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }}
    .badge {{
        background-color: #e6f3ed;
        color: #008a4f;
        padding: 4px 12px;
        border-radius: 15px;
        font-weight: bold;
        font-size: 0.8rem;
        margin-right: 5px;
        display: inline-block;
        margin-bottom: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. UI Layout
st.markdown(
    '<div class="main-header"><h1>🚌 Buss Intelligence Engine</h1><p>Data Engineering Lab Pipeline v1.0</p></div>',
    unsafe_allow_html=True)

col_input, col_result = st.columns([1, 1], gap="large")

with col_input:
    st.subheader("Raw Transit Data")
    raw_text = st.text_area("Passenger Feedback", height=150, placeholder="e.g., Line 1 was delayed at Munkegata...")
    process_btn = st.button("SUBMIT", use_container_width=True)

with col_result:
    st.subheader("LLM-aided Analysis")
    if process_btn and raw_text:
        with st.spinner("Invoking Local LLM (Quadro Accelerated)..."):
            try:
                # Backend Communication
                res = requests.post("http://backend:8000/analyze", json={"raw_text": raw_text})
                res.raise_for_status()
                data = res.json()
                analysis = data['analysis']

                # Displaying results
                st.markdown(f"""
                <div class="data-card">
                    <p style="color: #666; font-size: 0.8rem;">RECORD ID: {data['id'][:8]}</p>
                    <h3 style="margin-bottom: 0.5rem; color: #333;">{analysis['category']}</h3>
                    <p style="color: {'#d32f2f' if analysis['sentiment'] == 'Negative' else '#2e7d32'}; font-weight: bold; margin-bottom: 1rem;">
                        {analysis['sentiment']} Sentiment
                    </p>
                    <hr style="margin: 1rem 0;"/>
                    <p><b>Priority Level:</b> {'🔴' * analysis['priority']}</p>
                    <p style="margin-bottom: 0.5rem;"><b>Extracted Entities:</b></p>
                    {''.join([f'<span class="badge">{e}</span>' for e in analysis['extracted_entities']])}
                </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Engine connection failed. Check if Backend/Ollama are up. Error: {e}")
    else:
        st.info("Awaiting input for analysis...")
