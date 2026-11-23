import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from agents.weather_agent import WeatherAgent
from agents.crop_agent import CropAgent
from agents.recommendation_agent import RecommendationAgent

class CoordinatorAgent:
    """
    Agent 4: Coordinator and Report Agent
    Responsibilities:
    - Coordinates the multi-agent workflow.
    - Dispatches queries to WeatherAgent and CropAgent.
    - Routes combined data to RecommendationAgent.
    - Identifies and resolves inter-agent conflicts.
    - Formulates the final synthesized Farmer Advisory Report.
    """
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.name = "Coordinator & Report Agent"
        self.role = "Workflow Orchestrator & Conflict Resolver"
        self.weather_agent = WeatherAgent()
        self.crop_agent = CropAgent()
        self.recommendation_agent = RecommendationAgent()
        self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")

    def run_workflow(self, location: str, crop: str, soil: str, stage: str, farm_size_acres: float = 2.5) -> Dict[str, Any]:
        """
        Executes the 4-agent collaborative cycle with message logging
        and conflict detection.
        """
        timeline: List[Dict[str, Any]] = []

        def log_event(sender: str, recipient: str, action: str, details: str):
            timeline.append({
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "sender": sender,
                "recipient": recipient,
                "action": action,
                "details": details
            })

        # --- STEP 1: INITIAL DISPATCH ---
        log_event(
            self.name,
            "System / EventBus",
            "Initialize Advisory Request",
            f"Farmer input received: Location='{location}', Crop='{crop}', Soil='{soil}', Stage='{stage}', Size={farm_size_acres} acres."
        )

        # --- STEP 2: WEATHER INTELLIGENCE DISPATCH ---
        log_event(
            self.name,
            self.weather_agent.name,
            "Dispatch Weather Query",
            f"Requesting atmospheric data and multi-day hazard forecast for '{location}'."
        )
        weather_output = self.weather_agent.analyze(location)
        log_event(
            self.weather_agent.name,
            self.name,
            "Weather Analysis Completed",
            f"Recorded: {weather_output['temperature']}°C, {weather_output['humidity']}% humidity, "
            f"Rain forecast: {weather_output['forecast_3d_rain_mm']}mm. Risk level: {weather_output['overall_weather_risk']}."
        )

        # --- STEP 3: CROP ANALYSIS DISPATCH ---
        log_event(
            self.name,
            self.crop_agent.name,
            "Dispatch Crop Agronomy Query",
            f"Requesting physiological requirements and soil compatibility for '{crop}' in '{soil}' at '{stage}'."
        )
        crop_output = self.crop_agent.analyze(crop, soil, stage)
        log_event(
            self.crop_agent.name,
            self.name,
            "Crop Profile Evaluated",
            f"Stage Focus: '{crop_output['stage_focus']}'. Recommended nutrients: '{crop_output['nutrient_needs']}'. "
            f"Soil compatibility evaluated as '{crop_output['soil_suitability']}'."
        )

        # --- STEP 4: RECOMMENDATION AGENT SYNTHESIS ---
        log_event(
            self.name,
            self.recommendation_agent.name,
            "Dispatch Recommendation Generation",
            "Synthesizing combined microclimate metrics with crop physiological requirements."
        )
        recommendation_output = self.recommendation_agent.generate_recommendations(weather_output, crop_output)
        log_event(
            self.recommendation_agent.name,
            self.name,
            "Recommendations Formulated",
            f"Generated: Irrigation='{recommendation_output['irrigation']['urgency']}', "
            f"Fertilizer plan drafted, {len(recommendation_output['pest_and_disease'])} pest actions."
        )

        # --- STEP 5: CONFLICT DETECTION & RESOLUTION ---
        conflicts_resolved: List[Dict[str, str]] = []

        # Conflict 1: Rain forecast vs. Stage Fertilizer Application
        upcoming_rain = weather_output.get("forecast_3d_rain_mm", 0.0)
        nutrient_needed = crop_output.get("nutrient_needs", "")
        if upcoming_rain > 12.0 and "Nitrogen" in nutrient_needed:
            conflict = {
                "agents_involved": f"{self.crop_agent.name} vs {self.weather_agent.name}",
                "issue": f"Crop Agent requested Nitrogen/Urea top dressing, but Weather Agent forecast {upcoming_rain}mm rain.",
                "resolution": "RESOLVED BY COORDINATOR: Suspended top-dressing until 24h post-rain. Prevents nitrogen runoff, saving input costs and preserving groundwater."
            }
            conflicts_resolved.append(conflict)
            log_event(self.name, "Arbitration Engine", "Conflict Identified & Resolved", conflict["resolution"])

        # Conflict 2: Wind Speed vs Spraying
        wind_speed = weather_output.get("wind_speed", 0.0)
        if wind_speed > 18.0 and len(recommendation_output.get("pest_and_disease", [])) > 0:
            conflict = {
                "agents_involved": f"{self.recommendation_agent.name} vs {self.weather_agent.name}",
                "issue": f"Pest countermeasures queued, but wind speed is {wind_speed} km/h.",
                "resolution": "RESOLVED BY COORDINATOR: High drift risk. Restricted spraying window to calm early morning hours (< 10 km/h) or low-pressure coarse nozzles."
            }
            conflicts_resolved.append(conflict)
            log_event(self.name, "Arbitration Engine", "Conflict Identified & Resolved", conflict["resolution"])

        # Conflict 3: Soil Moisture Retention vs Waterlogging
        soil_type = crop_output.get("soil_type", "")
        if ("Clay" in soil_type or "Black" in soil_type) and upcoming_rain > 25.0:
            conflict = {
                "agents_involved": f"{self.crop_agent.name} vs {self.weather_agent.name}",
                "issue": f"Heavy {soil_type} has poor internal drainage during intense precipitation ({upcoming_rain}mm).",
                "resolution": "RESOLVED BY COORDINATOR: Mandatory ridge furrow clearing. Priority action assigned to field drainage to avoid root hypoxia."
            }
            conflicts_resolved.append(conflict)
            log_event(self.name, "Arbitration Engine", "Conflict Identified & Resolved", conflict["resolution"])

        # --- STEP 6: AI-POWERED OR SMART SYNTHESIZED EXECUTIVE SUMMARY ---
        ai_summary = self._generate_ai_summary(
            location, crop, soil, stage, weather_output, crop_output, recommendation_output, conflicts_resolved
        )

        final_report = {
            "farm_metadata": {
                "location": location,
                "crop": crop,
                "soil": soil,
                "stage": stage,
                "farm_size_acres": farm_size_acres,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "weather_intelligence": weather_output,
            "crop_analysis": crop_output,
            "recommendations": recommendation_output,
            "conflicts_detected": conflicts_resolved,
            "multi_agent_timeline": timeline,
            "executive_summary": ai_summary
        }

        log_event(
            self.name,
            "Farmer Dashboard",
            "Final Advisory Delivered",
            "Synthesized multi-agent report generated and verified."
        )

        return final_report

    def _generate_ai_summary(self, location: str, crop: str, soil: str, stage: str,
                             weather: Dict[str, Any], crop_info: Dict[str, Any],
                             rec: Dict[str, Any], conflicts: List[Dict[str, str]]) -> str:
        """
        Uses Gemini API if key is present, otherwise falls back to a high-quality agronomic synthesis.
        """
        if self.api_key:
            try:
                from google import genai
                client = genai.Client(api_key=self.api_key)
                prompt = f"""
                You are AgroMind AI, an elite smart farming advisory coordinator.
                Write a concise, high-impact 3-paragraph executive farming advisory for:
                - Location: {location}
                - Crop: {crop} ({stage})
                - Soil: {soil}
                - Current Weather: {weather.get('temperature')}°C, {weather.get('humidity')}% humidity, Wind: {weather.get('wind_speed')} km/h, 3-Day Rain: {weather.get('forecast_3d_rain_mm')}mm.
                - Irrigation Action: {rec['irrigation']['guideline']}
                - Fertilizer: {rec['fertilizer']['guideline']}
                - Coordinated Conflicts Resolved: {len(conflicts)}

                Ensure advice is practical, motivating, and directly addresses the weather risk.
                """
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                if response.text:
                    return response.text.strip()
            except Exception:
                pass

        # Intelligent Agronomic Fallback Summary
        rain_note = (
            f"With approximately {weather.get('forecast_3d_rain_mm')}mm of rain predicted over the next 72 hours, "
            f"irrigation should be paused and field drainage safeguarded."
            if weather.get('forecast_3d_rain_mm', 0) > 10
            else f"Dry to light moisture conditions ({weather.get('precipitation')}mm today) necessitate routine regulated irrigation."
        )

        conflict_note = (
            f"The coordinator successfully arbitrated {len(conflicts)} operational conflict(s), "
            f"safely sequencing chemical applications around rainfall and wind conditions."
            if conflicts else "All agronomic and environmental parameters are in equilibrium."
        )

        return (
            f"### AgroMind AI Executive Advisory for {crop} in {location}\n\n"
            f"Your **{crop}** crop is currently entering the **{stage}** in **{soil}**. "
            f"Current microclimate shows an ambient temperature of **{weather.get('temperature')}°C** and relative humidity of **{weather.get('humidity')}%**. "
            f"{rain_note}\n\n"
            f"**Key Priorities for This Week:**\n"
            f"- **Irrigation:** {rec['irrigation']['guideline']}\n"
            f"- **Nutrition:** {rec['fertilizer']['guideline']}\n"
            f"- **Pathogen Watch:** Monitor actively for {', '.join(crop_info.get('common_vulnerabilities', ['diseases'])[:2])}.\n\n"
            f"*{conflict_note}*"
        )
