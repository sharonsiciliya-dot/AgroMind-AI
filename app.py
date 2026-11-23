import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Direct agent imports for fallback if standalone
from agents.coordinator import CoordinatorAgent
from services.gemini_service import GeminiService

# --- CONFIG & STYLING ---
st.set_page_config(
    page_title="AgroMind AI - Smart Farming Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://localhost:8000"

# Inject modern UI styling inspired by the Smart Farming design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Top Header Container */
    .top-hero {
        background: linear-gradient(135deg, #1e4620 0%, #2e6930 50%, #438e47 100%);
        border-radius: 20px;
        padding: 24px 30px;
        color: #ffffff;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px rgba(30, 70, 32, 0.15);
    }
    .top-hero h1 {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 4px;
        color: #ffffff !important;
    }
    .top-hero .subtitle {
        color: #dcedc8;
        font-size: 1.02rem;
        margin-bottom: 12px;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 8px;
    }
    .badge-backend-on { background: #e8f5e9; color: #1b5e20; border: 1px solid #c8e6c9; }
    .badge-backend-off { background: #fff8e1; color: #f57f17; border: 1px solid #ffe082; }
    .badge-gemini-on { background: #e3f2fd; color: #0d47a1; border: 1px solid #bbdefb; }
    .badge-gemini-off { background: #f5f5f5; color: #616161; border: 1px solid #e0e0e0; }

    /* Weather Hero Card (Inspired by Design Mockup) */
    .weather-card {
        background: linear-gradient(135deg, #2d5a27 0%, #3e7b36 100%);
        border-radius: 20px;
        padding: 24px;
        color: #ffffff;
        box-shadow: 0 8px 20px rgba(45, 90, 39, 0.2);
        margin-bottom: 24px;
    }
    .weather-location {
        font-size: 1rem;
        font-weight: 600;
        color: #dcedc8;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .weather-temp {
        font-size: 3.4rem;
        font-weight: 700;
        line-height: 1.1;
        margin: 8px 0 16px 0;
    }
    .telemetry-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        background: rgba(255, 255, 255, 0.12);
        padding: 14px;
        border-radius: 14px;
        backdrop-filter: blur(8px);
    }
    .telemetry-item {
        text-align: center;
    }
    .telemetry-item .label {
        font-size: 0.78rem;
        color: #e8f5e9;
        margin-bottom: 2px;
    }
    .telemetry-item .val {
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
    }

    /* Section Headers */
    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1b5e20;
        margin: 20px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Commodity / Crop Card */
    .crop-pill-btn {
        background: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 16px;
        padding: 12px 8px;
        text-align: center;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .crop-pill-btn:hover {
        border-color: #2e7d32;
        transform: translateY(-2px);
    }

    /* Field Info Card */
    .field-card {
        background: #ffffff;
        border: 1px solid #e8f5e9;
        border-radius: 16px;
        padding: 18px 22px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }

    /* Advisory & Alert Boxes */
    .advisory-box {
        background: #ffffff;
        border-radius: 14px;
        border: 1px solid #e0e0e0;
        border-left: 6px solid #2e7d32;
        padding: 18px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .conflict-box {
        background: #fff8e1;
        border-radius: 14px;
        border: 1px solid #ffe082;
        border-left: 6px solid #f57f17;
        padding: 16px;
        margin-bottom: 12px;
    }
    .timeline-item {
        border-left: 3px solid #81c784;
        padding-left: 18px;
        padding-bottom: 14px;
        position: relative;
    }
    .timeline-item::before {
        content: "";
        width: 12px;
        height: 12px;
        background: #2e7d32;
        border-radius: 50%;
        position: absolute;
        left: -7.5px;
        top: 2px;
    }
</style>
""", unsafe_allow_html=True)

# --- BACKEND CONNECTION HELPER ---
@st.cache_data(ttl=5)
def check_backend_health():
    try:
        res = requests.get(f"{BACKEND_URL}/health", timeout=1.5)
        if res.status_code == 200:
            return True, res.json()
    except Exception:
        pass
    return False, {}

backend_online, backend_meta = check_backend_health()
gemini_active = backend_meta.get("gemini_api_configured", False) if backend_online else GeminiService().is_configured()

# --- TOP HERO BANNER ---
backend_badge = '<span class="status-badge badge-backend-on">🟢 Backend API Connected</span>' if backend_online else '<span class="status-badge badge-backend-off">🟡 Direct Engine Mode</span>'
gemini_badge = '<span class="status-badge badge-gemini-on">✨ Gemini AI Enabled</span>' if gemini_active else '<span class="status-badge badge-gemini-off">⚙️ Agronomic Rule Engine</span>'

today_str = datetime.now().strftime("%A, %d %b %Y")

st.markdown(f"""
<div class="top-hero">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1>Hello, Farmers 👋</h1>
            <div class="subtitle">🗓️ {today_str} &nbsp;|&nbsp; 🌾 AgroMind Multi-Agent Precision Agriculture System</div>
        </div>
        <div>
            {backend_badge}
            {gemini_badge}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR: FARM INPUTS ---
st.sidebar.markdown("### 🌾 Field & Location Settings")

# Quick Demo Scenario Buttons
st.sidebar.caption("⚡ Quick Demo Scenarios:")
p_col1, p_col2 = st.sidebar.columns(2)
preset = None
if p_col1.button("🍚 Mangaluru Rice", use_container_width=True):
    preset = {"location": "Mangaluru", "crop": "Rice", "soil": "Clay soil", "stage": "Vegetative / Growing stage"}
if p_col2.button("🌾 Punjab Wheat", use_container_width=True):
    preset = {"location": "Ludhiana", "crop": "Wheat", "soil": "Loamy soil", "stage": "Flowering / Panicle stage"}

p_col3, p_col4 = st.sidebar.columns(2)
if p_col3.button("☁️ Nagpur Cotton", use_container_width=True):
    preset = {"location": "Nagpur", "crop": "Cotton", "soil": "Black soil", "stage": "Vegetative / Growing stage"}
if p_col4.button("🍅 Bangalore Tomato", use_container_width=True):
    preset = {"location": "Bengaluru", "crop": "Tomato", "soil": "Red soil", "stage": "Flowering / Panicle stage"}

# Default values
default_loc = preset["location"] if preset else "Mangaluru"
crops = ["Rice", "Wheat", "Corn / Maize", "Cotton", "Tomato"]
soils = ["Clay soil", "Loamy soil", "Sandy soil", "Black soil", "Red soil"]
stages = [
    "Seedling / Germination",
    "Vegetative / Growing stage",
    "Flowering / Panicle stage",
    "Harvesting / Maturity"
]

default_crop_idx = crops.index(preset["crop"]) if preset and preset["crop"] in crops else 0
default_soil_idx = soils.index(preset["soil"]) if preset and preset["soil"] in soils else 0
default_stage_idx = stages.index(preset["stage"]) if preset and preset["stage"] in stages else 1

location_input = st.sidebar.text_input("📍 Farm Location / District", value=default_loc)
selected_crop = st.sidebar.selectbox("🌱 Crop Variety", crops, index=default_crop_idx)
selected_soil = st.sidebar.selectbox("🧱 Soil Classification", soils, index=default_soil_idx)
selected_stage = st.sidebar.selectbox("📈 Crop Growth Stage", stages, index=default_stage_idx)
field_area = st.sidebar.number_input("📐 Field Area (Acres)", min_value=0.5, max_value=500.0, value=2.5, step=0.5)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 Backend & AI Settings")
if backend_online:
    st.sidebar.success(f"Connected to Backend: `{BACKEND_URL}`")
else:
    st.sidebar.info(f"Backend offline. Run `python run_backend.py` to start REST server. (Running internal agents).")

key_override = st.sidebar.text_input("🔑 Gemini API Key (Optional Override)", type="password", help="Overrides GEMINI_API_KEY from backend .env")

run_analysis = st.sidebar.button("🚀 Analyze Farm & Run Agents", type="primary", use_container_width=True)

# --- BACKEND / AGENT CALL DISPATCH ---
def fetch_advisory(loc, crp, sl, stg, acres, key):
    payload = {
        "location": loc,
        "crop": crp,
        "soil": sl,
        "stage": stg,
        "farm_size_acres": acres,
        "gemini_api_key": key if key else None
    }
    # 1. Try Backend API first
    if backend_online:
        try:
            resp = requests.post(f"{BACKEND_URL}/api/advisory", json=payload, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                data["_source"] = "FastAPI Backend Server (http://localhost:8000)"
                return data
        except Exception:
            pass

    # 2. Fallback to direct agent execution
    coordinator = CoordinatorAgent(gemini_api_key=key if key else None)
    data = coordinator.run_workflow(loc, crp, sl, stg, acres)
    data["_source"] = "Standalone Direct Coordinator"
    return data

# Trigger analysis on first load or button click
if "advisory_data" not in st.session_state or run_analysis:
    with st.spinner("🤖 Coordinated Agents analyzing live weather, soil physics & crop requirements..."):
        st.session_state["advisory_data"] = fetch_advisory(
            location_input, selected_crop, selected_soil, selected_stage, field_area, key_override
        )

report = st.session_state["advisory_data"]
weather = report.get("weather_intelligence", {})
crop_info = report.get("crop_analysis", {})
recs = report.get("recommendations", {})
conflicts = report.get("conflicts_detected", [])
timeline = report.get("multi_agent_timeline", [])

# --- HERO WEATHER CARD (Matching Mockup Design) ---
temp_val = weather.get("temperature", 28.0)
humidity_val = weather.get("humidity", 65.0)
wind_val = weather.get("wind_speed", 12.0)
rain_val = weather.get("precipitation", 0.0)
soil_temp = weather.get("soil_temp_est", 26.5)

st.markdown(f"""
<div class="weather-card">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div class="weather-location">📍 {weather.get('location', location_input)}</div>
        <div style="font-size: 0.85rem; color: #dcedc8;">⚡ Powered by Open-Meteo Telemetry</div>
    </div>
    <div style="display: flex; justify-content: space-between; align-items: flex-end;">
        <div>
            <div class="weather-temp">+{temp_val}°C</div>
            <div style="color: #e8f5e9; font-size: 0.95rem;">Microclimate Hazard Risk: <strong>{weather.get('overall_weather_risk', 'LOW')}</strong></div>
        </div>
        <div style="text-align: right; margin-bottom: 12px;">
            <span style="font-size: 2.2rem;">⛅</span>
        </div>
    </div>
    <div class="telemetry-grid">
        <div class="telemetry-item">
            <div class="label">🌡️ Soil Temp</div>
            <div class="val">+{soil_temp}°C</div>
        </div>
        <div class="telemetry-item">
            <div class="label">💧 Humidity</div>
            <div class="val">{humidity_val}%</div>
        </div>
        <div class="telemetry-item">
            <div class="label">💨 Wind Speed</div>
            <div class="val">{wind_val} km/h</div>
        </div>
        <div class="telemetry-item">
            <div class="label">🌧️ 3D Rain Sum</div>
            <div class="val">{weather.get('forecast_3d_rain_mm', 0.0)} mm</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- COMMODITIES & FOOD SELECTION CAROUSEL ---
st.markdown('<div class="section-title">🌾 Commodities and Food</div>', unsafe_allow_html=True)
c_cols = st.columns(5)
crop_icons = {
    "Rice": "🍚",
    "Wheat": "🌾",
    "Corn / Maize": "🌽",
    "Cotton": "☁️",
    "Tomato": "🍅"
}

for i, crop_name in enumerate(crops[:5]):
    with c_cols[i]:
        is_active = (crop_name == selected_crop)
        border_col = "#2e7d32" if is_active else "#e0e0e0"
        bg_col = "#e8f5e9" if is_active else "#ffffff"
        st.markdown(f"""
        <div style="background: {bg_col}; border: 2px solid {border_col}; border-radius: 14px; padding: 12px 6px; text-align: center;">
            <div style="font-size: 1.8rem; margin-bottom: 2px;">{crop_icons.get(crop_name, '🌱')}</div>
            <div style="font-size: 0.88rem; font-weight: 600; color: #1b5e20;">{crop_name.split('/')[0].strip()}</div>
        </div>
        """, unsafe_allow_html=True)

# --- MY FIELDS STATUS ---
st.markdown('<div class="section-title">🚜 Field Status & Intelligence</div>', unsafe_allow_html=True)
f_col1, f_col2, f_col3, f_col4 = st.columns(4)
f_col1.metric("Field Variety", f"{selected_crop}")
f_col2.metric("Soil Classification", f"{selected_soil}")
f_col3.metric("Growth Stage", f"{selected_stage.split('/')[0].strip()}")
f_col4.metric("Est. Yield Potential", "6,800 - 7,500 kg/ha", "Optimal")

st.write("")

# --- TABS FOR MULTI-AGENT ADVISORY ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📋 Action Advisory",
    "💬 Ask AgroMind AI (Chat)",
    "🔄 Multi-Agent Event Bus",
    "⚖️ Conflict Arbitration",
    "🌦️ 3-Day Microclimate",
    "📥 Export Advisory"
])

# ================= TAB 1: ACTION ADVISORY =================
with tab1:
    st.markdown(report.get("executive_summary", "Advisory summary loading..."))

    st.markdown("### 🚜 Coordinated Action Directives")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div class="advisory-box">
            <h4>💧 Irrigation Protocol</h4>
        """, unsafe_allow_html=True)
        st.info(recs.get("irrigation", {}).get("guideline", "Maintain standard irrigation."))
        st.markdown(f"**Urgency:** `{recs.get('irrigation', {}).get('urgency', 'NORMAL')}` | **Soil Drainage:** {crop_info.get('soil_properties', {}).get('drainage', 'Standard')}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="advisory-box">
            <h4>🌱 Soil Nutrition & Fertilization</h4>
        """, unsafe_allow_html=True)
        st.success(recs.get("fertilizer", {}).get("guideline", "Apply recommended nutrients."))
        if recs.get("fertilizer", {}).get("caution"):
            st.warning(recs["fertilizer"]["caution"])
        st.markdown(f"**Stage Focus:** {crop_info.get('stage_focus', 'Vegetative growth')}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="advisory-box">
            <h4>🛡️ Pest & Pathogen Protection</h4>
        """, unsafe_allow_html=True)
        for pest in recs.get("pest_and_disease", []):
            st.markdown(f"**🎯 Target:** `{pest['target']}`")
            st.markdown(f"- *Trigger:* {pest['risk_trigger']}")
            st.markdown(f"- *Action:* {pest['action']}")
            st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="advisory-box">
            <h4>🚜 Daily Field Operation Feasibility</h4>
        """, unsafe_allow_html=True)
        for op_name, op_details in recs.get("field_operations", {}).items():
            icon = "✅" if op_details.get("permitted", True) else "🛑"
            st.markdown(f"**{icon} {op_name.replace('_', ' ').title()}:** {op_details.get('reason')}")
        st.markdown("</div>", unsafe_allow_html=True)

# ================= TAB 2: ASK AGROMIND AI (CHAT) =================
with tab2:
    st.markdown("### 💬 Ask AgroMind AI")
    st.caption("Ask questions about your farm, crop care, spraying feasibility, or fertilizer timing. Answers are generated by Google Gemini AI with live field telemetry injected.")

    sample_questions = [
        f"Can I spray pesticide on my {selected_crop} today?",
        f"Why should I postpone fertilizer if rain is forecast?",
        f"What are the best biological remedies for pests at {selected_stage}?",
        f"How does {selected_soil} affect my watering schedule?"
    ]

    selected_sample = st.selectbox("💡 Quick Sample Questions:", ["Select a question..."] + sample_questions)
    default_q = selected_sample if selected_sample != "Select a question..." else ""
    user_query = st.text_input("Your question:", value=default_q, placeholder="e.g. Is it safe to apply nitrogen fertilizer tomorrow?")

    if st.button("Ask Gemini Agent", type="primary"):
        if user_query:
            with st.spinner("🤖 AgroMind AI reasoning with field telemetry..."):
                context_payload = {
                    "location": location_input,
                    "crop": selected_crop,
                    "soil": selected_soil,
                    "stage": selected_stage,
                    "temperature": temp_val,
                    "humidity": humidity_val,
                    "rain_mm": weather.get("forecast_3d_rain_mm", 0.0)
                }
                
                # Check backend API first
                answer_text = ""
                source_label = ""
                if backend_online:
                    try:
                        q_resp = requests.post(
                            f"{BACKEND_URL}/api/ask",
                            json={"question": user_query, "context": context_payload, "gemini_api_key": key_override if key_override else None},
                            timeout=10
                        )
                        if q_resp.status_code == 200:
                            data = q_resp.json()
                            answer_text = data.get("answer", "")
                            source_label = f"Backend API ({data.get('powered_by', 'Gemini AI')})"
                    except Exception:
                        pass
                
                if not answer_text:
                    gem_svc = GeminiService(api_key=key_override if key_override else None)
                    answer_text = gem_svc.answer_question(user_query, context_payload)
                    source_label = "Direct Gemini Engine"

                st.markdown(f"""
                <div style="background: #f1f8e9; border: 1px solid #c8e6c9; border-radius: 14px; padding: 18px; margin-top: 14px;">
                    <div style="font-size: 0.85rem; color: #2e7d32; font-weight: 600; margin-bottom: 6px;">✨ {source_label} Response:</div>
                    <div style="font-size: 1rem; color: #1b5e20; line-height: 1.6;">{answer_text}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("Please enter or select a question first.")

# ================= TAB 3: AGENT EVENT BUS =================
with tab3:
    st.markdown("### 🔄 Live Multi-Agent Communication Bus")
    st.caption("Inspect the chronological message payload passing between the independent agents.")

    for event in timeline:
        st.markdown(f"""
        <div class="timeline-item">
            <span style="color: #616161; font-size: 0.8rem;">[{event['timestamp']}]</span>
            <strong style="color: #1b5e20;"> {event['sender']}</strong> ➔ 
            <strong style="color: #0d47a1;"> {event['recipient']}</strong>
            <br/>
            <span style="font-weight: 600; color: #212121;">Action: {event['action']}</span>
            <p style="margin-top: 4px; margin-bottom: 0; color: #424242; font-size: 0.95rem;">{event['details']}</p>
        </div>
        """, unsafe_allow_html=True)

# ================= TAB 4: CONFLICT ARBITRATION =================
with tab4:
    st.markdown("### ⚖️ Inter-Agent Conflict Detection & Resolution")
    st.write("Demonstrates how the Coordinator arbitrates competing priorities between weather volatility and rigid agronomic schedules.")

    if conflicts:
        for idx, conf in enumerate(conflicts, 1):
            st.markdown(f"""
            <div class="conflict-box">
                <h4 style="color: #d84315; margin-bottom: 6px;">⚡ Conflict #{idx}: {conf['agents_involved']}</h4>
                <p><strong>Divergent Condition:</strong> {conf['issue']}</p>
                <div style="background: #ffffff; padding: 12px; border-radius: 8px; border: 1px solid #ffe0b2;">
                    <strong style="color: #2e7d32;">{conf['resolution']}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No operational conflicts detected. All agent directives are fully aligned.")

# ================= TAB 5: 3-DAY MICROCLIMATE =================
with tab5:
    st.markdown("### 🌦️ Open-Meteo Atmospheric Forecast")
    forecast = weather.get("forecast", [])
    if forecast:
        df_weather = pd.DataFrame(forecast)
        df_weather.columns = ["Date", "Max Temp (°C)", "Min Temp (°C)", "Rainfall (mm)", "Rain Probability (%)"]
        st.dataframe(df_weather, use_container_width=True)
        st.line_chart(df_weather.set_index("Date")[["Max Temp (°C)", "Min Temp (°C)"]])

    st.markdown("### 🧱 Soil Physics Breakdown")
    s_props = crop_info.get("soil_properties", {})
    s1, s2 = st.columns(2)
    s1.metric("Estimated Soil Temp", f"{soil_temp} °C")
    s1.metric("Soil Saturation Index", f"{weather.get('soil_moisture_est', 50.0)} %")
    s2.write(f"**Soil Type:** {crop_info.get('soil_type')}")
    s2.write(f"**Water Holding Capacity:** {s_props.get('water_retention')}")
    s2.write(f"**Drainage Capacity:** {s_props.get('drainage')}")
    s2.write(f"**Fertilizer Adjustment:** {s_props.get('irrigation_adjustment')}")

# ================= TAB 6: EXPORT =================
with tab6:
    st.markdown("### 📥 Download Advisory Report")
    report_md = f"""# AgroMind AI Advisory Report
Generated on: {report.get('farm_metadata', {}).get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}
Location: {location_input} | Field Area: {field_area} Acres
Crop: {selected_crop} ({selected_stage}) | Soil: {selected_soil}
Data Source: {report.get('_source', 'AgroMind Multi-Agent Engine')}

---
## Executive Summary
{report.get('executive_summary', '')}

---
## Prescriptions
- Irrigation: {recs.get('irrigation', {}).get('guideline', '')}
- Nutrition: {recs.get('fertilizer', {}).get('guideline', '')}
"""
    st.download_button(
        label="📄 Download Markdown Advisory (.MD)",
        data=report_md,
        file_name=f"AgroMind_Advisory_{selected_crop}_{location_input}.md",
        mime="text/markdown",
        use_container_width=True
    )
    st.code(report_md, language="markdown")
