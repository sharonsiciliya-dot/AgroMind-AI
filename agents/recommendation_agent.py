from typing import Dict, Any, List

class RecommendationAgent:
    """
    Agent 3: Farm Recommendation Agent
    Responsibilities:
    - Combines outputs from Weather Agent and Crop Agent.
    - Produces synthesized, actionable farming recommendations:
      1. Irrigation Schedule (timing, volume, drainage adjustments)
      2. Fertilizer & Soil Nutrition Plan
      3. Pest & Disease Protective Action
      4. Daily Field Activity Advisory (Spraying, Weeding, Harvesting)
    """
    def __init__(self):
        self.name = "Farm Recommendation Agent"
        self.role = "Precision Agronomy & Decision Support Specialist"

    def generate_recommendations(self, weather_data: Dict[str, Any], crop_data: Dict[str, Any]) -> Dict[str, Any]:
        temp = weather_data.get("temperature", 28.0)
        humidity = weather_data.get("humidity", 65.0)
        upcoming_rain = weather_data.get("forecast_3d_rain_mm", 0.0)
        max_rain_prob = weather_data.get("max_rain_prob", 20)
        wind_speed = weather_data.get("wind_speed", 10.0)
        can_spray = weather_data.get("can_spray_today", True)

        crop_name = crop_data.get("crop", "Rice")
        growth_stage = crop_data.get("growth_stage", "Vegetative / Growing stage")
        soil_type = crop_data.get("soil_type", "Clay soil")
        soil_props = crop_data.get("soil_properties", {})
        vulnerabilities = crop_data.get("common_vulnerabilities", [])

        # --- 1. IRRIGATION ADVISORY ---
        irrigation_action = ""
        irrigation_urgency = "NORMAL"

        if "Harvesting" in growth_stage:
            irrigation_action = "🛑 DRAIN & STOP IRRIGATION: The crop is at maturity/harvesting stage. Field must be dried 10-14 days prior to harvest to facilitate equipment access and grain hardening."
            irrigation_urgency = "CRITICAL"
        elif upcoming_rain > 20.0 or max_rain_prob >= 75:
            irrigation_action = f"⏸️ SUSPEND IRRIGATION: Significant precipitation ({upcoming_rain}mm, {max_rain_prob}% probability) is imminent over the next 48-72h. Natural rainfall will meet crop evapotranspiration."
            if "Clay" in soil_type or "Black" in soil_type:
                irrigation_action += " Clear drainage ditches immediately to prevent root zone waterlogging."
            irrigation_urgency = "HIGH"
        elif upcoming_rain > 8.0:
            irrigation_action = f"⏳ REDUCE IRRIGATION: Moderate rainfall ({upcoming_rain}mm) expected. Provide only light deficit irrigation if soil surface is dry."
            irrigation_urgency = "MEDIUM"
        elif temp >= 35.0:
            if "Sandy" in soil_type:
                irrigation_action = "💧 FREQUENT LIGHT CYCLES: Extreme heat with high drainage soil requires daily early morning/evening drip irrigation to counter high evapotranspiration."
            else:
                irrigation_action = "💧 INCREASE IRRIGATION: Heat stress alert. Irrigate in early morning or evening to preserve soil moisture and cool the crop canopy."
            irrigation_urgency = "HIGH"
        else:
            irrigation_action = f"✅ MAINTAIN REGULAR REGIME: {crop_data.get('water_guideline', 'Standard watering')}. Adjust according to {soil_props.get('irrigation_adjustment', 'soil moisture')}."

        # --- 2. FERTILIZER & NUTRITION ADVISORY ---
        fertilizer_action = ""
        fertilizer_caution = ""

        if "Harvesting" in growth_stage:
            fertilizer_action = "🚫 NO FERTILIZER: Growth cycle completed; no further nutrient uptake needed."
        elif upcoming_rain > 15.0:
            fertilizer_action = f"⏸️ POSTPONE APPLICATION: Next nutrient target is: '{crop_data.get('nutrient_needs')}'. However, hold application until after rains pass to prevent nutrient runoff and leaching."
            fertilizer_caution = "Surface runoff hazard: Rain will wash away unincorporated fertilizers."
        else:
            fertilizer_action = f"🌱 APPLY RECOMMENDED NUTRIENTS: Stage requirement: {crop_data.get('nutrient_needs')}."
            if "Sandy" in soil_type:
                fertilizer_action += " Split nitrogen doses into 2-3 smaller applications to mitigate leaching."

        # --- 3. PEST & DISEASE MANAGEMENT ---
        pest_actions: List[Dict[str, str]] = []
        is_fungal_threat = (humidity >= 78.0 and 22.0 <= temp <= 32.0)

        if is_fungal_threat:
            pest_actions.append({
                "target": "Fungal Complex (Blight / Mildew / Rot)",
                "risk_trigger": f"High humidity ({humidity}%) & warm temperature ({temp}°C)",
                "action": "Prophylactic application of bio-fungicide (Trichoderma viride @ 5g/L) or copper oxychloride spray when foliage dries."
            })

        for vuln in vulnerabilities[:2]:
            pest_actions.append({
                "target": vuln,
                "risk_trigger": f"Stage susceptibility at {growth_stage}",
                "action": f"Scout field twice weekly for early signs of {vuln}. Use pheromone traps or neem-based repellent (Azadirachtin 10,000 ppm)."
            })

        # --- 4. FIELD ACTIVITIES DISPATCH ---
        activities = {
            "pesticide_spraying": {
                "permitted": can_spray and upcoming_rain < 5.0,
                "reason": "Permitted: Calm wind and dry canopy" if (can_spray and upcoming_rain < 5.0) else f"Hold spray: Wind {wind_speed} km/h or rain {upcoming_rain}mm will cause drift or wash-off."
            },
            "intercultural_weeding": {
                "permitted": upcoming_rain < 15.0 and "Clay" not in soil_type or upcoming_rain < 5.0,
                "reason": "Favorable soil workability" if upcoming_rain < 10.0 else "Soil may be too muddy/sticky for tractor or mechanical weeding."
            },
            "field_drainage_check": {
                "permitted": True,
                "urgency": "Urgent" if upcoming_rain > 15.0 else "Routine",
                "reason": "Ensure discharge pathways are free of debris before rainfall events."
            }
        }

        return {
            "agent": self.name,
            "role": self.role,
            "irrigation": {
                "guideline": irrigation_action,
                "urgency": irrigation_urgency
            },
            "fertilizer": {
                "guideline": fertilizer_action,
                "caution": fertilizer_caution
            },
            "pest_and_disease": pest_actions,
            "field_operations": activities,
            "summary": (
                f"Recommendations synthesized: Irrigation={irrigation_urgency}; "
                f"Fertilizer aligned with {growth_stage}; {len(pest_actions)} pest/pathogen countermeasures queued."
            )
        }
