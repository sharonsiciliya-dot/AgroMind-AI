import requests
from typing import Dict, Any, Optional

class WeatherService:
    """
    Fetches real-time and forecast weather data using Open-Meteo API
    with automatic geocoding and resilient fallback data.
    """
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    # Common fallback coordinates for major agricultural hubs
    FALLBACK_COORDINATES = {
        "mangaluru": {"lat": 12.9141, "lon": 74.8560, "name": "Mangaluru, Karnataka, India"},
        "bengaluru": {"lat": 12.9716, "lon": 77.5946, "name": "Bengaluru, Karnataka, India"},
        "punjab": {"lat": 31.1471, "lon": 75.3412, "name": "Punjab, India"},
        "ludhiana": {"lat": 30.9010, "lon": 75.8573, "name": "Ludhiana, Punjab, India"},
        "nagpur": {"lat": 21.1458, "lon": 79.0882, "name": "Nagpur, Maharashtra, India"},
        "hyderabad": {"lat": 17.3850, "lon": 78.4867, "name": "Hyderabad, Telangana, India"},
        "patna": {"lat": 25.5941, "lon": 85.1376, "name": "Patna, Bihar, India"},
        "lucknow": {"lat": 26.8467, "lon": 80.9462, "name": "Lucknow, Uttar Pradesh, India"},
        "coimbatore": {"lat": 11.0168, "lon": 76.9558, "name": "Coimbatore, Tamil Nadu, India"}
    }

    @classmethod
    def get_coordinates(cls, location_name: str) -> Optional[Dict[str, Any]]:
        """Look up latitude and longitude for a city or region."""
        normalized = location_name.strip().lower()
        if normalized in cls.FALLBACK_COORDINATES:
            return cls.FALLBACK_COORDINATES[normalized]

        try:
            params = {
                "name": location_name,
                "count": 1,
                "language": "en",
                "format": "json"
            }
            resp = requests.get(cls.GEOCODING_URL, params=params, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if "results" in data and len(data["results"]) > 0:
                    item = data["results"][0]
                    name_parts = [item.get("name", "")]
                    if item.get("admin1"):
                        name_parts.append(item.get("admin1"))
                    if item.get("country"):
                        name_parts.append(item.get("country"))
                    return {
                        "lat": item["latitude"],
                        "lon": item["longitude"],
                        "name": ", ".join(name_parts)
                    }
        except Exception:
            pass

        # Return default fallback if network lookup fails
        return cls.FALLBACK_COORDINATES.get(normalized, {
            "lat": 12.9141,
            "lon": 74.8560,
            "name": f"{location_name.capitalize()} (Estimated)"
        })

    @classmethod
    def get_weather(cls, location_name: str) -> Dict[str, Any]:
        """Fetch current weather and next 3-day forecast."""
        geo = cls.get_coordinates(location_name)
        lat = geo["lat"]
        lon = geo["lon"]
        display_name = geo["name"]

        try:
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "rain",
                    "weather_code",
                    "wind_speed_10m",
                    "wind_direction_10m"
                ],
                "daily": [
                    "weather_code",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "wind_speed_10m_max"
                ],
                "timezone": "auto"
            }
            resp = requests.get(cls.WEATHER_URL, params=params, timeout=6)
            if resp.status_code == 200:
                w_data = resp.json()
                curr = w_data.get("current", {})
                daily = w_data.get("daily", {})

                # Estimate soil moisture and temperature from current 2m temp and humidity
                current_temp = curr.get("temperature_2m", 28.0)
                current_humidity = curr.get("relative_humidity_2m", 65.0)
                rain_now = curr.get("rain", 0.0)
                wind_spd = curr.get("wind_speed_10m", 12.0)

                soil_temp_est = round(current_temp * 0.92, 1)
                soil_moisture_est = round(min(100.0, max(15.0, (current_humidity * 0.5) + (rain_now * 10))), 1)

                forecast_days = []
                times = daily.get("time", [])
                max_temps = daily.get("temperature_2m_max", [])
                min_temps = daily.get("temperature_2m_min", [])
                rain_sums = daily.get("precipitation_sum", [])
                pop_max = daily.get("precipitation_probability_max", [])

                for i in range(min(4, len(times))):
                    forecast_days.append({
                        "date": times[i],
                        "temp_max": max_temps[i] if i < len(max_temps) else current_temp,
                        "temp_min": min_temps[i] if i < len(min_temps) else current_temp - 5,
                        "rain_sum": rain_sums[i] if i < len(rain_sums) else 0.0,
                        "rain_prob": pop_max[i] if i < len(pop_max) else 10
                    })

                return {
                    "source": "Open-Meteo Live API",
                    "location": display_name,
                    "latitude": lat,
                    "longitude": lon,
                    "temperature": current_temp,
                    "humidity": current_humidity,
                    "precipitation": rain_now,
                    "wind_speed": wind_spd,
                    "soil_temp_est": soil_temp_est,
                    "soil_moisture_est": soil_moisture_est,
                    "forecast": forecast_days,
                    "status": "success"
                }
        except Exception as e:
            # Resilient fallback mock data for testing/offline
            pass

        return {
            "source": "AgroMind Meteorological Simulation (Offline Fallback)",
            "location": display_name,
            "latitude": lat,
            "longitude": lon,
            "temperature": 29.5,
            "humidity": 78.0,
            "precipitation": 3.2,
            "wind_speed": 14.5,
            "soil_temp_est": 26.8,
            "soil_moisture_est": 62.0,
            "forecast": [
                {"date": "Day 1 (Today)", "temp_max": 31.0, "temp_min": 24.0, "rain_sum": 4.5, "rain_prob": 70},
                {"date": "Day 2", "temp_max": 30.5, "temp_min": 23.5, "rain_sum": 8.0, "rain_prob": 85},
                {"date": "Day 3", "temp_max": 32.0, "temp_min": 24.5, "rain_sum": 0.5, "rain_prob": 25}
            ],
            "status": "fallback"
        }
