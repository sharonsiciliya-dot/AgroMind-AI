import uvicorn

if __name__ == "__main__":
    print("🌾 Starting AgroMind AI Backend Server on http://localhost:8000 ...")
    print("📖 Interactive API Docs available at http://localhost:8000/docs")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
