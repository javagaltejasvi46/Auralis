#!/usr/bin/env python3
"""
Auralis Backend Startup Script
Handles auto-configuration and server startup
"""

import sys
import os
import time
import subprocess
import signal
from pathlib import Path
from auto_config import configure_network

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'faster-whisper',
        'ollama'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies satisfied")
    return True

def check_ollama():
    """Check if Ollama is running and has the required model"""
    print("\n🤖 Checking Ollama...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            if "phi3:mini" in model_names:
                print("✅ Ollama is running with phi3:mini model")
                return True
            else:
                print("⚠️  Ollama is running but phi3:mini model not found")
                print("Run: ollama pull phi3:mini")
                return False
        else:
            print("❌ Ollama is not responding")
            return False
    except Exception as e:
        print(f"❌ Ollama check failed: {e}")
        print("Please start Ollama: ollama serve")
        return False

def start_transcription_server():
    """Start the transcription WebSocket server"""
    print("\n🎤 Starting transcription server...")
    
    try:
        # Start transcription server in background
        transcription_process = subprocess.Popen([
            sys.executable, "transcription_server.py"
        ], cwd=Path(__file__).parent)
        
        # Give it a moment to start
        time.sleep(2)
        
        # Check if it's still running
        if transcription_process.poll() is None:
            print("✅ Transcription server started (PID: {})".format(transcription_process.pid))
            return transcription_process
        else:
            print("❌ Transcription server failed to start")
            return None
    except Exception as e:
        print(f"❌ Failed to start transcription server: {e}")
        return None

def start_api_server(host="0.0.0.0", port=8002):
    """Start the main API server"""
    print(f"\n🚀 Starting API server on {host}:{port}...")
    
    try:
        # Start API server
        subprocess.run([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", host,
            "--port", str(port),
            "--reload"
        ], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")

def create_env_file():
    """Create .env file with current configuration"""
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("📝 Creating .env file...")
        
        # Get current IP
        from auto_config import get_local_ip
        local_ip = get_local_ip()
        
        env_content = f"""# Auralis Backend Configuration
LOCAL_IP={local_ip}
API_HOST=0.0.0.0
API_PORT=8002
WS_PORT=8003
OLLAMA_URL=http://localhost:11434
PHI3_MODEL=phi3:mini
DATABASE_URL=sqlite:///./auralis.db
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✅ Created .env file with IP: {local_ip}")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n🛑 Shutting down servers...")
    sys.exit(0)

def main():
    """Main startup function"""
    print("=" * 60)
    print("🎯 AURALIS BACKEND STARTUP")
    print("=" * 60)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create .env file
    create_env_file()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Configure network
    local_ip = configure_network()
    
    # Check Ollama (optional - continue without it)
    ollama_available = check_ollama()
    if not ollama_available:
        print("⚠️  Continuing without Ollama (AI features will be limited)")
    
    # Start transcription server
    transcription_process = start_transcription_server()
    
    try:
        # Start API server (this blocks)
        start_api_server()
    finally:
        # Cleanup
        if transcription_process and transcription_process.poll() is None:
            print("🛑 Stopping transcription server...")
            transcription_process.terminate()
            transcription_process.wait()

if __name__ == "__main__":
    main()