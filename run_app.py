import sys
import os
import time
import threading
import uvicorn
from pyngrok import ngrok, conf

# Use existing ngrok configuration with saved authtoken
user_ngrok_config = os.path.expandvars(r"%LOCALAPPDATA%\ngrok\ngrok.yml")
if os.path.exists(user_ngrok_config):
    conf.get_default().config_path = user_ngrok_config

def start_server():
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    print("\n" + "="*65)
    print("🌱 AgroMind AI — Starting Multi-Agent Server & Public Tunnel")
    print("="*65)

    # 1. Start Uvicorn in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1.5)

    # 2. Start Ngrok Tunnel
    public_url = None
    try:
        tunnel = ngrok.connect(8000, "http")
        public_url = tunnel.public_url

        print("\n" + "*"*65)
        print(f"🚀 PUBLIC TUNNEL URL : {public_url}")
        print(f"🌾 LOCAL URL         : http://localhost:8000")
        print(f"📖 API DOCS          : {public_url}/docs")
        print("*"*65 + "\n")
        print("💡 Share this Public URL with team members or judges.")
        print("Press Ctrl+C in this terminal to stop.\n")

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down AgroMind AI tunnel...")
        if public_url:
            ngrok.disconnect(public_url)
        ngrok.kill()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Tunnel error: {e}")
        print("You can still use the local URL: http://localhost:8000")
        while True:
            time.sleep(1)
