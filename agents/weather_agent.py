from typing import Dict, Any, List
from services.weather_api import WeatherService

class WeatherAgent:
    """
    Agent 1: Weather Intelligence Agent
    Responsibilities:
    - Collects live weather data via Open-Meteo.
    - Analyzes temperature, rainfall, humidity, wind, and forecast conditions.
    - Identifies agricultural risks: Heat Stress, Frost/Cold Shock, Waterlogging,
      Fungal Disease favorable conditions, High Evaporation, and Spraying drift risks.
    """
    def __init__(self):
        self.name = "Weather Intelligence Agent"
        self.role = "Atmospheric & Microclimate Risk Analyzer"

    def analyze(self, location: str) -> Dict[str, Any]:
        weather_raw = WeatherService.get_weather(location)

        temp = weather_raw.get("temperature", 28.0)
        humidity = weather_raw.get("humidity", 60.0)
        precipitation = weather_raw.get("precipitation", 0.0)
        wind_speed = weather_raw.get("wind_speed", 10.0)
        forecast = weather_raw.get("forecast", [])

        # Calculate forecast rain sum over next 72 hours
        upcoming_rain_sum = sum(day.get("rain_sum", 0.0) for day in forecast[:3])
        max_rain_prob = max((day.get("rain_prob", 0) for day in forecast[:3]), default=0)

        # Risk assessments
        risks: List[Dict[str, str]] = []
        alerts: List[str] = []

        # 1. Temperature Risk
        if temp >= 38.0:
            risks.append({
                "type": "Extreme Heat Stress",
                "severity": "HIGH",
                "detail": f"Ambient temperature is {temp}°C. Significant risk of pollen sterility and wilting."
            })
            alerts.append(f"⚠️ Extreme Heat ({temp}°C): Provide protective shade or frequent light irrigation.")
        elif temp >= 34.0:
            risks.append({
                "type": "Moderate Heat Stress",
                "severity": "MEDIUM",
                "detail": f"Current temp is {temp}°C with accelerated moisture depletion."
            })
        elif temp <= 10.0:
            risks.append({
                "type": "Cold/Chilling Injury",
                "severity": "HIGH",
                "detail": f"Low temperature ({temp}°C) will stunt vegetative progress."
            })
            alerts.append(f"❄️ Cold Advisory ({temp}°C): Risk of growth dormancy.")

        # 2. Precipitation & Waterlogging Risk
        if upcoming_rain_sum > 35.0 or precipitation > 15.0:
            risks.append({
                "type": "Excessive Rainfall & Waterlogging",
                "severity": "HIGH",
                "detail": f"Next 3-day rainfall accumulation is ~{upcoming_rain_sum:.1f}mm. High risk of root rot & surface runoff."
            })
            alerts.append(f"🌧️ Flood/Waterlogging Risk: Ensure active field drainage channels.")
        elif upcoming_rain_sum > 15.0 or max_rain_prob >= 70:
            risks.append({
                "type": "Moderate Rain Impending",
                "severity": "MEDIUM",
                "detail": f"Expected rain {upcoming_rain_sum:.1f}mm with {max_rain_prob}% probability."
            })

        # 3. Fungal Disease Risk Index (Combined Humidity + Temp)
        if humidity >= 80.0 and 22.0 <= temp <= 32.0:
            risks.append({
                "type": "High Fungal Pathogen Vulnerability",
                "severity": "HIGH",
                "detail": f"Humidity ({humidity}%) and temperature ({temp}°C) create optimal conditions for blast, mildew, and blight."
            })
            alerts.append(f"🍄 Disease Outbreak Warning: Warm & humid weather promotes fungal pathogen multiplication.")
        elif humidity >= 70.0:
            risks.append({
                "type": "Moderate Pathogen Pressure",
                "severity": "LOW",
                "detail": f"Humidity is elevated at {humidity}%."
            })

        # 4. Wind & Agrochemical Spraying Risk
        can_spray = True
        if wind_speed > 20.0:
            can_spray = False
            risks.append({
                "type": "High Wind Drift Risk",
                "severity": "MEDIUM",
                "detail": f"Wind speed of {wind_speed} km/h causes pesticide and foliar fertilizer drift off-target."
            })
            alerts.append(f"💨 High Wind Speed ({wind_speed} km/h): Postpone foliar spraying.")

        # Determine overall risk level
        severities = [r["severity"] for r in risks]
        if "HIGH" in severities:
            overall_risk = "HIGH"
        elif "MEDIUM" in severities:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"

        return {
            "agent": self.name,
            "role": self.role,
            "location": weather_raw.get("location", location),
            "temperature": temp,
            "humidity": humidity,
            "precipitation": precipitation,
            "wind_speed": wind_speed,
            "soil_temp_est": weather_raw.get("soil_temp_est", 26.0),
            "soil_moisture_est": weather_raw.get("soil_moisture_est", 50.0),
            "forecast_3d_rain_mm": round(upcoming_rain_sum, 1),
            "max_rain_prob": max_rain_prob,
            "forecast": forecast,
            "can_spray_today": can_spray,
            "identified_risks": risks,
            "alerts": alerts,
            "overall_weather_risk": overall_risk,
            "summary": (
                f"Conditions at {weather_raw.get('location', location)}: {temp}°C, {humidity}% humidity, "
                f"wind {wind_speed} km/h. Next 3-day rainfall expectation is {upcoming_rain_sum:.1f}mm "
                f"with {max_rain_prob}% probability. Overall weather hazard is {overall_risk}."
            )
        }
