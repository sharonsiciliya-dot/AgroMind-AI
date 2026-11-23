import uvicorn
import webbrowser
import os

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🌱 AgroMind AI — Multi-Agent Smart Farming System")
    print("="*60)
    print("🌾 Dashboard URL : http://localhost:8000")
    print("📖 API Docs URL  : http://localhost:8000/docs")
    print("🤖 AI Engine     : Google Gemini AI + Autonomous Agents")
    print("🛰️ Weather Feed  : Open-Meteo Live API")
    print("="*60 + "\n")

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
