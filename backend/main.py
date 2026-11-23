import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from agents.coordinator import CoordinatorAgent
from agents.weather_agent import WeatherAgent
from agents.crop_agent import CropAgent
from services.gemini_service import GeminiService

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AgroMind AI - Multi-Agent Smart Farming Backend API",
    description="RESTful API & Web Application coordinating autonomous agricultural AI agents with live Open-Meteo telemetry and conflict arbitration.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to frontend assets
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Request Models
class AdvisoryRequest(BaseModel):
    location: str = Field(default="Mangaluru", description="Farm location/city name")
    crop: str = Field(default="Rice", description="Crop variety name")
    soil: str = Field(default="Clay soil", description="Soil type")
    stage: str = Field(default="Vegetative / Growing stage", description="Crop growth stage")
    farm_size_acres: float = Field(default=2.5, ge=0.1, le=10000.0, description="Field size in acres")
    gemini_api_key: Optional[str] = Field(default=None, description="Optional override for API Key")

class QuestionRequest(BaseModel):
    question: str = Field(..., description="Farmer's question")
    context: Dict[str, Any] = Field(default_factory=dict, description="Current field and weather context")
    gemini_api_key: Optional[str] = Field(default=None, description="Optional override for API Key")

class AddCropRequest(BaseModel):
    name: str = Field(..., description="Name of crop / food item (e.g. Potato, Olive, Grapes)")
    icon: Optional[str] = Field(default="🌱", description="Emoji icon (e.g. 🥔, 🫒, 🍇)")
    water_need: Optional[str] = Field(default="Medium", description="Low, Medium, or High")
    best_soil: Optional[str] = Field(default="Loamy soil", description="Preferred soil classification")
    ideal_min: Optional[int] = Field(default=18, description="Minimum ideal temperature in °C")
    ideal_max: Optional[int] = Field(default=30, description="Maximum ideal temperature in °C")

# Global instances of agents and services
weather_agent = WeatherAgent()
crop_agent = CropAgent()
gemini_service = GeminiService()

# --- SERVE FRONTEND AT ROOT ---
@app.get("/")
def serve_frontend():
    """Serves the AgroMind modern Web UI dashboard."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "service": "AgroMind AI",
        "status": "online",
        "docs": "/docs"
    }

# --- API ENDPOINTS ---
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "active_agents": [
            "Weather Intelligence Agent",
            "Crop Analysis Agent",
            "Farm Recommendation Agent",
            "Coordinator & Report Agent"
        ],
        "ai_engine_active": gemini_service.is_configured()
    }

@app.get("/api/ai/status")
def ai_status():
    """Checks the status of the backend AI integration."""
    return gemini_service.test_connection()

@app.get("/api/weather")
def get_weather(location: str = Query(..., description="City or district name")):
    """Endpoint for Weather Intelligence Agent."""
    try:
        data = weather_agent.analyze(location)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weather analysis failed: {str(e)}")

@app.get("/api/crops")
def get_crop_data():
    """Returns available crop profiles, growth stages, and soil properties."""
    crops_list = []
    for name, data in crop_agent.crop_database.items():
        crops_list.append({
            "name": name,
            "icon": data.get("icon", "🌱"),
            "water_need": data.get("water_need", "Medium"),
            "best_soils": data.get("best_soils", ["Loamy soil"])
        })
    return {
        "crops": crops_list,
        "available_crops": list(crop_agent.crop_database.keys()),
        "available_soils": list(crop_agent.soil_properties.keys()),
        "stages": [
            "Seedling / Germination",
            "Vegetative / Growing stage",
            "Flowering / Panicle stage",
            "Harvesting / Maturity"
        ]
    }

@app.post("/api/crops")
def add_crop(req: AddCropRequest):
    """
    Registers a new crop / food item dynamically into the Crop Agent database.
    """
    try:
        new_profile = crop_agent.register_crop(
            name=req.name,
            icon=req.icon or "🌱",
            water_need=req.water_need or "Medium",
            best_soil=req.best_soil or "Loamy soil",
            ideal_min=req.ideal_min or 18,
            ideal_max=req.ideal_max or 30
        )
        return {
            "status": "success",
            "message": f"Crop '{req.name}' successfully added to AgroMind knowledge base.",
            "crop": {
                "name": req.name,
                "icon": req.icon or "🌱",
                "water_need": req.water_need or "Medium",
                "profile": new_profile
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register crop: {str(e)}")

@app.post("/api/advisory")
def generate_advisory(req: AdvisoryRequest):
    """
    Main Multi-Agent Coordination Endpoint:
    Dispatches tasks to WeatherAgent, CropAgent, RecommendationAgent,
    resolves operational conflicts, and synthesizes report with AI.
    """
    try:
        active_key = req.gemini_api_key or os.getenv("GEMINI_API_KEY")
        coordinator = CoordinatorAgent(gemini_api_key=active_key)

        # Ensure custom crop is registered in coordinator's crop agent as well
        if req.crop in crop_agent.crop_database and req.crop not in coordinator.crop_agent.crop_database:
            coordinator.crop_agent.crop_database[req.crop] = crop_agent.crop_database[req.crop]

        report = coordinator.run_workflow(
            location=req.location,
            crop=req.crop,
            soil=req.soil,
            stage=req.stage,
            farm_size_acres=req.farm_size_acres
        )
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Advisory orchestration failed: {str(e)}")

@app.post("/api/ask")
def ask_ai(req: QuestionRequest):
    """
    Farmer Conversational Q&A Endpoint:
    Provides context-aware answers to agricultural questions using the AgroMind AI Engine.
    """
    try:
        active_key = req.gemini_api_key or os.getenv("GEMINI_API_KEY")
        svc = GeminiService(api_key=active_key) if active_key else gemini_service
        answer = svc.answer_question(req.question, req.context)
        return {
            "question": req.question,
            "answer": answer,
            "powered_by": "AgroMind AI Engine"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question processing failed: {str(e)}")

# Mount static files for JS and assets
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
