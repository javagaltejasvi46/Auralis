#!/usr/bin/env python3
"""
AURALIS Setup Verification Script
Checks if all dependencies and requirements are properly installed
"""

import sys
import subprocess
import importlib.util

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and 10 <= version.minor < 14:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.10-3.13)")
        return False

def check_command(command, name):
    """Check if a command exists"""
    try:
        result = subprocess.run([command, "--version"], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"   ✅ {name}: {version}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    print(f"   ❌ {name} not found")
    return False

def check_python_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    spec = importlib.util.find_spec(import_name)
    if spec is not None:
        try:
            module = importlib.import_module(import_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"   ✅ {package_name}: {version}")
            return True
        except ImportError:
            pass
    print(f"   ❌ {package_name} not installed")
    return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("AURALIS Setup Verification")
    print("=" * 60)
    print()
    
    all_checks = []
    
    # Python version
    all_checks.append(check_python_version())
    print()
    
    # System commands
    print("🔧 Checking system commands...")
    all_checks.append(check_command("ffmpeg", "FFmpeg"))
    all_checks.append(check_command("node", "Node.js"))
    all_checks.append(check_command("npm", "npm"))
    print()
    
    # Core Python packages
    print("📦 Checking core Python packages...")
    all_checks.append(check_python_package("fastapi"))
    all_checks.append(check_python_package("uvicorn"))
    all_checks.append(check_python_package("websockets"))
    all_checks.append(check_python_package("sqlalchemy"))
    all_checks.append(check_python_package("pydantic"))
    all_checks.append(check_python_package("deep_translator", "deep_translator"))
    print()
    
    # Whisper packages
    print("🤖 Checking AI/ML packages...")
    all_checks.append(check_python_package("faster-whisper", "faster_whisper"))
    all_checks.append(check_python_package("ctranslate2"))
    all_checks.append(check_python_package("huggingface-hub", "huggingface_hub"))
    all_checks.append(check_python_package("tokenizers"))
    all_checks.append(check_python_package("av"))
    all_checks.append(check_python_package("numpy"))
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(all_checks)
    total = len(all_checks)
    
    if passed == total:
        print(f"✅ All checks passed! ({passed}/{total})")
        print()
        print("🎉 Your AURALIS setup is ready!")
        print()
        print("Next steps:")
        print("  1. Start backend API: python backend/main.py")
        print("  2. Start WebSocket: python backend/transcription_server.py")
        print("  3. Start frontend: cd frontend && npx expo start")
        return 0
    else:
        print(f"⚠️  Some checks failed ({passed}/{total} passed)")
        print()
        print("Please install missing dependencies:")
        print()
        print("System commands:")
        print("  - FFmpeg: winget install Gyan.FFmpeg.Essentials")
        print("  - Node.js: winget install OpenJS.NodeJS")
        print()
        print("Python packages:")
        print("  pip install -r backend/requirements.txt")
        print("  pip install -r backend/requirements_whisper.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
