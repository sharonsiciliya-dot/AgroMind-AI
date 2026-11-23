import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

class GeminiService:
    """
    Backend service for AgroMind AI integration.
    Handles synthesis of multi-agent recommendations, microclimate reasoning,
    and conversational agronomic Q&A for farmers.
    """
    SUPPORTED_MODELS = ['gemini-3.5-flash-lite', 'gemini-3.8-flash', 'gemini-2.5-flash']

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self._client = None
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception:
                self._client = None

    def is_configured(self) -> bool:
        return bool(self.api_key and self._client)

    def _call_model(self, contents: str) -> Optional[str]:
        if not self.is_configured():
            return None
        for model in self.SUPPORTED_MODELS:
            try:
                resp = self._client.models.generate_content(
                    model=model,
                    contents=contents
                )
                if resp and resp.text:
                    return resp.text.strip()
            except Exception:
                continue
        return None

    def test_connection(self) -> Dict[str, Any]:
        if not self.is_configured():
            return {
                "status": "unconfigured",
                "message": "API key is not set in backend .env. Rule-based agronomic engine active."
            }
        result = self._call_model("Hello, reply with 'AI Engine online for AgroMind'.")
        if result:
            return {
                "status": "connected",
                "message": result
            }
        return {
            "status": "error",
            "message": "AI connection attempt failed."
        }

    def synthesize_advisory(
        self,
        farm_metadata: Dict[str, Any],
        weather: Dict[str, Any],
        crop_info: Dict[str, Any],
        recommendations: Dict[str, Any],
        conflicts: List[Dict[str, str]]
    ) -> str:
        """
        Synthesizes an expert, multi-agent agronomic summary.
        Falls back to rule-based synthesis if AI service is unavailable.
        """
        if self.is_configured():
            prompt = f"""
            You are AgroMind AI, an elite agricultural scientist and precision farming consultant.
            Synthesize a clear, highly actionable farming advisory for this farmer:

            FARM DETAILS:
            - Location: {farm_metadata.get('location')}
            - Crop: {farm_metadata.get('crop')} (Stage: {farm_metadata.get('stage')})
            - Soil: {farm_metadata.get('soil')}
            - Field Size: {farm_metadata.get('farm_size_acres', 2.5)} Acres

            LIVE WEATHER (Open-Meteo):
            - Ambient Temp: {weather.get('temperature')}°C
            - Relative Humidity: {weather.get('humidity')}%
            - 3-Day Expected Rainfall: {weather.get('forecast_3d_rain_mm')} mm
            - Wind Speed: {weather.get('wind_speed')} km/h
            - Weather Risk Assessment: {weather.get('overall_weather_risk')}

            AGRONOMIC DIRECTIVES:
            - Target Nutrition: {crop_info.get('nutrient_needs')}
            - Soil Drainage: {crop_info.get('soil_properties', {}).get('drainage')}
            - Irrigation Action: {recommendations.get('irrigation', {}).get('guideline')}
            - Fertilizer Action: {recommendations.get('fertilizer', {}).get('guideline')}

            COORDINATED CONFLICTS ARBITRATED:
            {len(conflicts)} conflict(s) resolved:
            {self._format_conflicts(conflicts)}

            INSTRUCTIONS:
            1. Write 3 concise paragraphs formatted in clean Markdown with emojis.
            2. Explain the rationale for why certain actions are held or prioritized (e.g. rain vs fertilizer, wind vs spraying).
            3. Conclude with 3 clear bullet points: 'Top 3 Tasks for the Next 48 Hours'.
            """
            result = self._call_model(prompt)
            if result:
                return result

        # Resilient fallback synthesis
        return self._fallback_synthesis(farm_metadata, weather, crop_info, recommendations, conflicts)

    def answer_question(self, question: str, context: Dict[str, Any]) -> str:
        """
        Allows farmers to chat and ask follow-up questions to AgroMind AI
        with full farm context injected.
        """
        if self.is_configured():
            prompt = f"""
            You are AgroMind AI assistant talking to a farmer.
            CURRENT FIELD CONTEXT:
            - Location: {context.get('location', 'Unknown')}
            - Crop: {context.get('crop', 'Rice')} ({context.get('stage', 'Growing')})
            - Soil: {context.get('soil', 'Clay soil')}
            - Temperature: {context.get('temperature', 28)}°C, Humidity: {context.get('humidity', 65)}%, 3-Day Rain: {context.get('rain_mm', 0)}mm
            
            FARMER'S QUESTION:
            "{question}"

            Provide a direct, practical, and helpful answer in 2-3 short paragraphs with emojis.
            """
            result = self._call_model(prompt)
            if result:
                return result

        # Fallback response if no key configured
        return (
            f"Based on your {context.get('crop', 'crop')} at {context.get('stage', 'growth stage')} "
            f"in {context.get('location', 'your area')}, with temperature at {context.get('temperature', 28)}°C "
            f"and rain forecast of {context.get('rain_mm', 0)}mm: ensure regular soil moisture checks and monitor for pests."
        )

    def _format_conflicts(self, conflicts: List[Dict[str, str]]) -> str:
        if not conflicts:
            return "No conflicts detected."
        return "\n".join([f"- {c.get('agents_involved')}: {c.get('resolution')}" for c in conflicts])

    def _fallback_synthesis(self, meta: Dict[str, Any], weather: Dict[str, Any],
                            crop_info: Dict[str, Any], recs: Dict[str, Any],
                            conflicts: List[Dict[str, str]]) -> str:
        rain_note = (
            f"With approximately **{weather.get('forecast_3d_rain_mm')} mm** of rain predicted over the next 72 hours, "
            f"irrigation must be paused and field drainage safeguarded to prevent root waterlogging."
            if weather.get('forecast_3d_rain_mm', 0) > 10
            else f"Relatively dry conditions ({weather.get('precipitation')} mm precipitation) require scheduled irrigation to maintain canopy vigor."
        )

        conflict_note = (
            f"The Coordinator Agent successfully arbitrated **{len(conflicts)} operational conflict(s)**, "
            f"safely sequencing chemical applications around rainfall and wind conditions."
            if conflicts else "All agronomic and environmental parameters are in equilibrium."
        )

        vuln_text = ", ".join(crop_info.get('common_vulnerabilities', ['foliar pathogens'])[:2])

        return (
            f"### 🌱 AgroMind AI Executive Advisory for {meta.get('crop')} in {meta.get('location')}\n\n"
            f"Your **{meta.get('crop')}** crop is currently progressing through the **{meta.get('stage')}** in **{meta.get('soil')}**. "
            f"Local telemetry indicates an ambient temperature of **{weather.get('temperature')}°C** and relative humidity of **{weather.get('humidity')}%**. "
            f"{rain_note}\n\n"
            f"**🛡️ Agronomic Coordination Rationale:**\n"
            f"{conflict_note} Stage-specific focus is centered on *{crop_info.get('stage_focus')}*.\n\n"
            f"**📋 Top 3 Priorities for the Next 48 Hours:**\n"
            f"1. **Water Management:** {recs.get('irrigation', {}).get('guideline')}\n"
            f"2. **Fertilizer Protocol:** {recs.get('fertilizer', {}).get('guideline')}\n"
            f"3. **Pathogen Watch:** Scout canopy twice weekly for early symptoms of **{vuln_text}**."
        )
