import streamlit as st
import pandas as pd
import json
from datetime import datetime

from agents.coordinator import CoordinatorAgent

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AgroMind AI - Smart Farming Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR MODERN FARMING UI ---
st.markdown("""
<style>
    /* Main theme accents */
    :root {
        --primary-green: #2e7d32;
        --secondary-green: #4caf50;
        --accent-earth: #8d6e63;
        --card-bg: #ffffff;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #43a047 100%);
        padding: 24px;
        border-radius: 16px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: #ffffff !important;
        margin-bottom: 6px;
        font-weight: 700;
        font-size: 2.2rem;
    }
    .main-header p {
        color: #e8f5e9;
        font-size: 1.05rem;
        margin-bottom: 0;
    }
    
    .agent-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .agent-weather { background-color: #e3f2fd; color: #1565c0; border: 1px solid #bbdefb; }
    .agent-crop { background-color: #f1f8e9; color: #33691e; border: 1px solid #dcedc8; }
    .agent-rec { background-color: #fff8e1; color: #f57f17; border: 1px solid #ffe082; }
    .agent-coord { background-color: #f3e5f5; color: #6a1b9a; border: 1px solid #e1bee7; }
    
    .metric-card {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.03);
    }
    .metric-card .title { font-size: 0.85rem; color: #616161; margin-bottom: 4px; }
    .metric-card .value { font-size: 1.6rem; font-weight: 700; color: #1b5e20; }
    
    .advisory-box {
        border-left: 5px solid #2e7d32;
        background-color: #f9fbf9;
        padding: 16px 20px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 16px;
    }
    
    .conflict-box {
        border-left: 5px solid #e65100;
        background-color: #fff3e0;
        padding: 14px 18px;
        border-radius: 0 10px 10px 0;
        margin-bottom: 12px;
    }
    
    .timeline-item {
        border-left: 2px solid #a5d6a7;
        padding-left: 16px;
        padding-bottom: 14px;
        position: relative;
    }
    .timeline-item::before {
        content: "●";
        color: #2e7d32;
        position: absolute;
        left: -6px;
        top: -2px;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("""
<div class="main-header">
    <h1>🌱 AgroMind AI</h1>
    <p>Multi-Agent Collaborative Precision Farming Assistant — Live Microclimate, Soil Intelligence & Arbitrated Agronomic Decision Support</p>
</div>
""", unsafe_allow_html=True)

# --- SIDEBAR: FARM CONFIGURATION ---
st.sidebar.image("https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=600&q=80", caption="Smart Precision Agriculture", use_container_width=True)
st.sidebar.header("🌾 Farm & Field Setup")

# Preset buttons for fast hackathon demo
st.sidebar.subheader("⚡ Quick Demo Scenarios")
col_p1, col_p2 = st.sidebar.columns(2)
preset = None
if col_p1.button("🍚 Mangaluru Rice", use_container_width=True):
    preset = {"location": "Mangaluru", "crop": "Rice", "soil": "Clay soil", "stage": "Vegetative / Growing stage"}
if col_p2.button("🌾 Punjab Wheat", use_container_width=True):
    preset = {"location": "Ludhiana", "crop": "Wheat", "soil": "Loamy soil", "stage": "Flowering / Panicle stage"}

col_p3, col_p4 = st.sidebar.columns(2)
if col_p3.button("☁️ Nagpur Cotton", use_container_width=True):
    preset = {"location": "Nagpur", "crop": "Cotton", "soil": "Black soil", "stage": "Vegetative / Growing stage"}
if col_p4.button("🍅 Bangalore Tomato", use_container_width=True):
    preset = {"location": "Bengaluru", "crop": "Tomato", "soil": "Red soil", "stage": "Flowering / Panicle stage"}

default_location = preset["location"] if preset else "Mangaluru"
default_crop_index = 0
default_soil_index = 0
default_stage_index = 1

crop_options = ["Rice", "Wheat", "Corn / Maize", "Cotton", "Tomato"]
soil_options = ["Clay soil", "Loamy soil", "Sandy soil", "Black soil", "Red soil"]
stage_options = [
    "Seedling / Germination",
    "Vegetative / Growing stage",
    "Flowering / Panicle stage",
    "Harvesting / Maturity"
]

if preset:
    if preset["crop"] in crop_options:
        default_crop_index = crop_options.index(preset["crop"])
    if preset["soil"] in soil_options:
        default_soil_index = soil_options.index(preset["soil"])
    if preset["stage"] in stage_options:
        default_stage_index = stage_options.index(preset["stage"])

location = st.sidebar.text_input("📍 Farm Location / City", value=default_location, help="Fetches live atmospheric data via Open-Meteo")
selected_crop = st.sidebar.selectbox("🌱 Crop Variety", crop_options, index=default_crop_index)
selected_soil = st.sidebar.selectbox("🧱 Soil Composition", soil_options, index=default_soil_index)
selected_stage = st.sidebar.selectbox("📈 Growth Stage", stage_options, index=default_stage_index)
farm_size = st.sidebar.number_input("📐 Field Size (Acres)", min_value=0.5, max_value=500.0, value=2.5, step=0.5)

st.sidebar.markdown("---")
gemini_key = st.sidebar.text_input("🔑 Gemini API Key (Optional)", type="password", help="Provides LLM executive summary; rule-based engine is always active without a key")

run_btn = st.sidebar.button("🚀 Run Multi-Agent Advisory", type="primary", use_container_width=True)

# Session state persistence
if "report" not in st.session_state or run_btn:
    coordinator = CoordinatorAgent(gemini_api_key=gemini_key)
    with st.spinner("🤖 Coordinated Agents analyzing live weather, soil physics & crop requirements..."):
        st.session_state["report"] = coordinator.run_workflow(
            location=location,
            crop=selected_crop,
            soil=selected_soil,
            stage=selected_stage,
            farm_size_acres=farm_size
        )

report = st.session_state["report"]
weather = report["weather_intelligence"]
crop_info = report["crop_analysis"]
recs = report["recommendations"]
conflicts = report["conflicts_detected"]
timeline = report["multi_agent_timeline"]

# --- AGENT TEAM BANNER ---
st.markdown("""
<div style="margin-bottom: 20px;">
    <span class="agent-pill agent-weather">🛰️ Agent 1: Weather Intelligence</span>
    <span class="agent-pill agent-crop">🔬 Agent 2: Crop Agronomy</span>
    <span class="agent-pill agent-rec">💡 Agent 3: Farm Recommendation</span>
    <span class="agent-pill agent-coord">⚖️ Agent 4: Coordinator & Conflict Resolver</span>
</div>
""", unsafe_allow_html=True)

# --- LIVE METRIC CARDS ---
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="title">🌡️ Ambient Temp</div>
        <div class="value">{weather.get('temperature', 28.0)}°C</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="title">💧 Humidity</div>
        <div class="value">{weather.get('humidity', 65.0)}%</div>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="title">🌧️ 3-Day Rain Forecast</div>
        <div class="value">{weather.get('forecast_3d_rain_mm', 0.0)} mm</div>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="title">💨 Wind Velocity</div>
        <div class="value">{weather.get('wind_speed', 10.0)} km/h</div>
    </div>
    """, unsafe_allow_html=True)
with col5:
    risk_color = "#c62828" if weather.get("overall_weather_risk") == "HIGH" else ("#ef6c00" if weather.get("overall_weather_risk") == "MEDIUM" else "#2e7d32")
    st.markdown(f"""
    <div class="metric-card">
        <div class="title">⚠️ Microclimate Risk</div>
        <div class="value" style="color: {risk_color};">{weather.get('overall_weather_risk', 'LOW')}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- TABS FOR MULTI-AGENT ADVISORY ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Action Advisory & Report",
    "🤖 Multi-Agent Live Exchange",
    "⚖️ Conflict Arbitration Engine",
    "🌦️ Weather & Soil Diagnostics",
    "📥 Download Submission Report"
])

# ================= TAB 1: ACTION ADVISORY =================
with tab1:
    st.markdown(report["executive_summary"])

    st.markdown("### 🚜 Tactical Field Operations Matrix")
    c_left, c_right = st.columns(2)

    with c_left:
        st.markdown("""
        <div class="advisory-box">
            <h4>💧 Irrigation Protocol</h4>
        """, unsafe_allow_html=True)
        st.info(recs["irrigation"]["guideline"])
        st.markdown(f"**Urgency:** `{recs['irrigation']['urgency']}` | **Soil Drainage:** {crop_info['soil_properties'].get('drainage')}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="advisory-box">
            <h4>🌱 Soil Nutrition & Fertilization</h4>
        """, unsafe_allow_html=True)
        st.success(recs["fertilizer"]["guideline"])
        if recs["fertilizer"].get("caution"):
            st.warning(recs["fertilizer"]["caution"])
        st.markdown(f"**Stage Focus:** {crop_info.get('stage_focus')}")
        st.markdown("</div>", unsafe_allow_html=True)

    with c_right:
        st.markdown("""
        <div class="advisory-box">
            <h4>🛡️ Pest & Pathogen Countermeasures</h4>
        """, unsafe_allow_html=True)
        for pest in recs.get("pest_and_disease", []):
            st.markdown(f"**🎯 Target:** `{pest['target']}`")
            st.markdown(f"- *Trigger:* {pest['risk_trigger']}")
            st.markdown(f"- *Recommended Action:* {pest['action']}")
            st.markdown("---")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <div class="advisory-box">
            <h4>🚜 Daily Activity Feasibility</h4>
        """, unsafe_allow_html=True)
        ops = recs.get("field_operations", {})
        for op_name, op_details in ops.items():
            status_icon = "✅" if op_details.get("permitted", True) else "🛑"
            clean_name = op_name.replace("_", " ").title()
            st.markdown(f"**{status_icon} {clean_name}:** {op_details.get('reason')}")
        st.markdown("</div>", unsafe_allow_html=True)

# ================= TAB 2: MULTI-AGENT EVENT TIMELINE =================
with tab2:
    st.markdown("### 🔄 Live Multi-Agent Communication Bus")
    st.caption("Inspect the actual chronological message payload passing between the independent agents.")

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

# ================= TAB 3: CONFLICT ARBITRATION =================
with tab3:
    st.markdown("### ⚖️ Inter-Agent Conflict Detection & Resolution")
    st.write(
        "A critical test of an authentic multi-agent system is how it arbitrates competing priorities "
        "(e.g., standard crop fertilizer schedules versus unpredictable rainfall washes)."
    )

    if conflicts:
        for idx, conf in enumerate(conflicts, 1):
            st.markdown(f"""
            <div class="conflict-box">
                <h4 style="color: #d84315; margin-bottom: 6px;">⚡ Conflict #{idx}: {conf['agents_involved']}</h4>
                <p><strong>Divergent Condition:</strong> {conf['issue']}</p>
                <div style="background: #ffffff; padding: 10px; border-radius: 6px; border: 1px solid #ffe0b2;">
                    <strong>{conf['resolution']}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No conflicting directives found. All agent parameters are fully harmonious.")

# ================= TAB 4: WEATHER & SOIL DIAGNOSTICS =================
with tab4:
    st.markdown("### 🌦️ Open-Meteo Atmospheric Forecast (3-Day Outlook)")
    forecast = weather.get("forecast", [])
    if forecast:
        df_weather = pd.DataFrame(forecast)
        df_weather.columns = ["Date", "Max Temp (°C)", "Min Temp (°C)", "Rainfall (mm)", "Rain Probability (%)"]
        st.dataframe(df_weather, use_container_width=True)
        st.line_chart(df_weather.set_index("Date")[["Max Temp (°C)", "Min Temp (°C)"]])
    
    st.markdown("### 🧱 Soil Profile Diagnostics")
    soil_props = crop_info.get("soil_properties", {})
    s_col1, s_col2 = st.columns(2)
    with s_col1:
        st.metric("Estimated Soil Temperature", f"{weather.get('soil_temp_est', 26.0)} °C")
        st.metric("Estimated Moisture Saturation", f"{weather.get('soil_moisture_est', 50.0)} %")
    with s_col2:
        st.write(f"**Soil Classification:** {crop_info.get('soil_type')}")
        st.write(f"**Water Holding Capacity:** {soil_props.get('water_retention')}")
        st.write(f"**Internal Drainage:** {soil_props.get('drainage')}")
        st.write(f"**CEC & Nutrient Retention:** {soil_props.get('nutrient_retention')}")

# ================= TAB 5: DOWNLOAD & SUBMISSION =================
with tab5:
    st.markdown("### 📥 Export Advisory Report for Field Log or Submission")
    
    # Generate clean markdown output
    report_md = f"""# AgroMind AI: Multi-Agent Smart Farming Advisory
Generated on: {report['farm_metadata']['generated_at']}
Location: {location} | Field Size: {farm_size} Acres
Crop: {selected_crop} | Stage: {selected_stage} | Soil: {selected_soil}

---
## 1. Executive Summary
{report['executive_summary']}

---
## 2. Microclimate Status
- Ambient Temperature: {weather.get('temperature')}°C
- Relative Humidity: {weather.get('humidity')}%
- Upcoming 3-Day Rain: {weather.get('forecast_3d_rain_mm')} mm (Probability: {weather.get('max_rain_prob')}%)
- Wind Velocity: {weather.get('wind_speed')} km/h
- Microclimate Hazard Rating: {weather.get('overall_weather_risk')}

---
## 3. Coordinated Prescriptions
### Irrigation:
{recs['irrigation']['guideline']} (Urgency: {recs['irrigation']['urgency']})

### Soil Fertility & Nutrition:
{recs['fertilizer']['guideline']}

### Pathogen Countermeasures:
"""
    for pest in recs.get("pest_and_disease", []):
        report_md += f"- **{pest['target']}**: {pest['action']} (Trigger: {pest['risk_trigger']})\n"

    report_md += f"""
---
## 4. Conflict Arbitration Summary
Total Conflicts Resolved: {len(conflicts)}
"""
    for c in conflicts:
        report_md += f"- {c['agents_involved']}: {c['resolution']}\n"

    st.download_button(
        label="📄 Download Full Advisory Report (.MD)",
        data=report_md,
        file_name=f"AgroMind_Advisory_{selected_crop}_{location}.md",
        mime="text/markdown",
        use_container_width=True
    )

    st.code(report_md, language="markdown")
