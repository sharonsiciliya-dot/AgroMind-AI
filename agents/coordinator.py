import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from agents.weather_agent import WeatherAgent
from agents.crop_agent import CropAgent
from agents.recommendation_agent import RecommendationAgent
from services.gemini_service import GeminiService

class CoordinatorAgent:
    """
    Agent 4: Coordinator and Report Agent
    Responsibilities:
    - Coordinates the multi-agent workflow.
    - Dispatches queries to WeatherAgent and CropAgent.
    - Routes combined data to RecommendationAgent.
    - Identifies and resolves inter-agent conflicts.
    - Synthesizes the final report using the backend Gemini AI service.
    """
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.name = "Coordinator & Report Agent"
        self.role = "Workflow Orchestrator & Conflict Resolver"
        self.weather_agent = WeatherAgent()
        self.crop_agent = CropAgent()
        self.recommendation_agent = RecommendationAgent()
        self.gemini_service = GeminiService(api_key=gemini_api_key)

    def run_workflow(self, location: str, crop: str, soil: str, stage: str, farm_size_acres: float = 2.5) -> Dict[str, Any]:
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
        meta = {
            "location": location,
            "crop": crop,
            "soil": soil,
            "stage": stage,
            "farm_size_acres": farm_size_acres,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        log_event(
            self.name,
            "EventBus",
            "Initialize Advisory Request",
            f"Farmer request received for {crop} ({stage}) in {soil} at {location} ({farm_size_acres} acres)."
        )

        # --- STEP 2: WEATHER INTELLIGENCE DISPATCH ---
        log_event(
            self.name,
            self.weather_agent.name,
            "Dispatch Weather Query",
            f"Retrieving atmospheric telemetry and forecast for '{location}'."
        )
        weather_output = self.weather_agent.analyze(location)
        log_event(
            self.weather_agent.name,
            self.name,
            "Weather Analysis Completed",
            f"Current: {weather_output['temperature']}°C, {weather_output['humidity']}% humidity. "
            f"3-Day Rain: {weather_output['forecast_3d_rain_mm']}mm. Risk level: {weather_output['overall_weather_risk']}."
        )

        # --- STEP 3: CROP ANALYSIS DISPATCH ---
        log_event(
            self.name,
            self.crop_agent.name,
            "Dispatch Crop Agronomy Query",
            f"Analyzing physiological requirements of {crop} ({stage}) in {soil}."
        )
        crop_output = self.crop_agent.analyze(crop, soil, stage)
        log_event(
            self.crop_agent.name,
            self.name,
            "Crop Profile Evaluated",
            f"Focus: '{crop_output['stage_focus']}'. Target: '{crop_output['nutrient_needs']}'. "
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
                "resolution": "RESOLVED BY COORDINATOR: Suspended top-dressing until 24h post-rain to avoid nutrient runoff and protect groundwater."
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

        # --- STEP 6: GEMINI AI SYNTHESIS IN BACKEND ---
        log_event(
            self.name,
            "Gemini AI Service",
            "Generate Executive Synthesis",
            "Invoking backend Gemini AI service for multi-agent synthesis."
        )

        ai_summary = self.gemini_service.synthesize_advisory(
            farm_metadata=meta,
            weather=weather_output,
            crop_info=crop_output,
            recommendations=recommendation_output,
            conflicts=conflicts_resolved
        )

        final_report = {
            "farm_metadata": meta,
            "weather_intelligence": weather_output,
            "crop_analysis": crop_output,
            "recommendations": recommendation_output,
            "conflicts_detected": conflicts_resolved,
            "multi_agent_timeline": timeline,
            "executive_summary": ai_summary,
            "gemini_active": self.gemini_service.is_configured()
        }

        log_event(
            self.name,
            "Farmer Dashboard",
            "Final Advisory Delivered",
            "Synthesized multi-agent report generated and verified."
        )

        return final_report
