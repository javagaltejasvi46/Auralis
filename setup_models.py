#!/usr/bin/env python3
"""
Auralis Model Setup Script
Checks and downloads required AI models (Phi-3-Mini and Faster-Whisper)
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    print_info("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}.{version.micro}")
        return False

def check_command_exists(command):
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None

def check_ollama_installed():
    """Check if Ollama is installed"""
    print_info("Checking for Ollama installation...")
    if check_command_exists("ollama"):
        print_success("Ollama is installed")
        return True
    else:
        print_warning("Ollama is not installed")
        return False

def install_ollama():
    """Install Ollama based on operating system"""
    print_header("Installing Ollama")
    
    system = platform.system()
    
    if system == "Windows":
        print_info("Please download and install Ollama from:")
        print_info("https://ollama.ai/download/windows")
        print_warning("After installation, restart this script")
        return False
    
    elif system == "Darwin":  # macOS
        print_info("Installing Ollama for macOS...")
        try:
            subprocess.run(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"], 
                         shell=True, check=True)
            print_success("Ollama installed successfully")
            return True
        except subprocess.CalledProcessError:
            print_error("Failed to install Ollama")
            print_info("Please install manually from: https://ollama.ai/download/mac")
            return False
    
    elif system == "Linux":
        print_info("Installing Ollama for Linux...")
        try:
            subprocess.run("curl -fsSL https://ollama.ai/install.sh | sh", 
                         shell=True, check=True)
            print_success("Ollama installed successfully")
            return True
        except subprocess.CalledProcessError:
            print_error("Failed to install Ollama")
            return False
    
    else:
        print_error(f"Unsupported operating system: {system}")
        return False

def check_ollama_running():
    """Check if Ollama service is running"""
    print_info("Checking if Ollama service is running...")
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print_success("Ollama service is running")
            return True
        else:
            print_warning("Ollama service is not running")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_warning("Ollama service is not running")
        return False

def start_ollama_service():
    """Start Ollama service"""
    print_info("Starting Ollama service...")
    
    system = platform.system()
    
    if system == "Windows":
        print_info("Please start Ollama from the Start Menu or system tray")
        input("Press Enter after starting Ollama...")
        return check_ollama_running()
    
    else:
        try:
            # Start Ollama in background
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            import time
            time.sleep(3)  # Wait for service to start
            
            if check_ollama_running():
                print_success("Ollama service started")
                return True
            else:
                print_error("Failed to start Ollama service")
                return False
        except Exception as e:
            print_error(f"Error starting Ollama: {e}")
            return False

def check_phi3_model():
    """Check if Phi-3-Mini model is downloaded"""
    print_info("Checking for Phi-3-Mini model...")
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, timeout=10)
        if "phi3" in result.stdout.lower():
            print_success("Phi-3-Mini model is already downloaded")
            return True
        else:
            print_warning("Phi-3-Mini model not found")
            return False
    except Exception as e:
        print_error(f"Error checking model: {e}")
        return False

def download_phi3_model():
    """Download Phi-3-Mini model via Ollama"""
    print_header("Downloading Phi-3-Mini Model")
    print_info("This may take 5-10 minutes depending on your internet speed...")
    print_info("Model size: ~2.5GB")
    
    try:
        # Pull phi3:mini model
        process = subprocess.Popen(
            ["ollama", "pull", "phi3:mini"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Print progress
        for line in process.stdout:
            print(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            print_success("Phi-3-Mini model downloaded successfully")
            return True
        else:
            print_error("Failed to download Phi-3-Mini model")
            return False
            
    except Exception as e:
        print_error(f"Error downloading model: {e}")
        return False

def test_phi3_model():
    """Test Phi-3-Mini model with a simple prompt"""
    print_info("Testing Phi-3-Mini model...")
    
    try:
        result = subprocess.run(
            ["ollama", "run", "phi3:mini", "Say 'Hello, I am Phi-3-Mini!'"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print_success("Phi-3-Mini model is working correctly")
            print_info(f"Response: {result.stdout.strip()[:100]}...")
            return True
        else:
            print_error("Phi-3-Mini model test failed")
            return False
            
    except subprocess.TimeoutExpired:
        print_error("Model test timed out")
        return False
    except Exception as e:
        print_error(f"Error testing model: {e}")
        return False

def check_whisper_model():
    """Check if Faster-Whisper model is downloaded"""
    print_info("Checking for Faster-Whisper model...")
    
    # Check cache directory
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    
    if cache_dir.exists():
        # Look for whisper model files
        whisper_models = list(cache_dir.glob("*whisper*"))
        if whisper_models:
            print_success("Faster-Whisper model found in cache")
            return True
    
    print_warning("Faster-Whisper model not found")
    return False

def download_whisper_model():
    """Download Faster-Whisper model"""
    print_header("Downloading Faster-Whisper Model")
    print_info("This may take 3-5 minutes...")
    print_info("Model size: ~1.5GB (medium model)")
    
    try:
        # Import and download
        print_info("Importing faster-whisper...")
        from faster_whisper import WhisperModel
        
        print_info("Downloading model...")
        model = WhisperModel("medium", device="cpu", compute_type="int8")
        
        print_success("Faster-Whisper model downloaded successfully")
        return True
        
    except ImportError:
        print_error("faster-whisper not installed")
        print_info("Installing faster-whisper...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "faster-whisper"],
                         check=True)
            print_success("faster-whisper installed")
            return download_whisper_model()  # Retry
        except subprocess.CalledProcessError:
            print_error("Failed to install faster-whisper")
            return False
    except Exception as e:
        print_error(f"Error downloading Whisper model: {e}")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    print_header("Checking Python Dependencies")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "faster-whisper",
        "websockets",
        "deep-translator"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print_success(f"{package} is installed")
        except ImportError:
            print_warning(f"{package} is not installed")
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(packages):
    """Install missing Python packages"""
    if not packages:
        return True
    
    print_header("Installing Missing Dependencies")
    print_info(f"Installing: {', '.join(packages)}")
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + packages,
            check=True
        )
        print_success("All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install some dependencies")
        return False

def create_models_directory():
    """Create models directory if it doesn't exist"""
    models_dir = Path("backend/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    print_success(f"Models directory created: {models_dir}")

def generate_summary_report():
    """Generate a summary report of the setup"""
    print_header("Setup Summary")
    
    # Check all components
    checks = {
        "Python 3.8+": check_python_version(),
        "Ollama Installed": check_ollama_installed(),
        "Ollama Running": check_ollama_running(),
        "Phi-3-Mini Model": check_phi3_model(),
        "Faster-Whisper Model": check_whisper_model()
    }
    
    print("\nComponent Status:")
    print("-" * 40)
    for component, status in checks.items():
        status_icon = "✓" if status else "✗"
        status_color = Colors.OKGREEN if status else Colors.FAIL
        print(f"{status_color}{status_icon} {component}{Colors.ENDC}")
    
    all_ready = all(checks.values())
    
    print("\n" + "=" * 40)
    if all_ready:
        print_success("All components are ready!")
        print_info("You can now start the backend servers:")
        print_info("  python backend/main.py")
        print_info("  python backend/transcription_server.py")
    else:
        print_warning("Some components are not ready")
        print_info("Please resolve the issues above")
    print("=" * 40 + "\n")
    
    return all_ready

def main():
    """Main setup function"""
    print_header("Auralis Model Setup")
    print_info(f"Operating System: {platform.system()}")
    print_info(f"Python Version: {sys.version.split()[0]}")
    
    # Step 1: Check Python version
    if not check_python_version():
        print_error("Please install Python 3.8 or higher")
        sys.exit(1)
    
    # Step 2: Check/Install Ollama
    if not check_ollama_installed():
        response = input("\nOllama is not installed. Install now? (y/n): ")
        if response.lower() == 'y':
            if not install_ollama():
                print_error("Please install Ollama manually and run this script again")
                sys.exit(1)
        else:
            print_error("Ollama is required. Exiting.")
            sys.exit(1)
    
    # Step 3: Start Ollama service
    if not check_ollama_running():
        response = input("\nOllama service is not running. Start now? (y/n): ")
        if response.lower() == 'y':
            if not start_ollama_service():
                print_error("Please start Ollama manually and run this script again")
                sys.exit(1)
        else:
            print_error("Ollama service must be running. Exiting.")
            sys.exit(1)
    
    # Step 4: Check/Download Phi-3 model
    if not check_phi3_model():
        response = input("\nPhi-3-Mini model not found. Download now? (y/n): ")
        if response.lower() == 'y':
            if not download_phi3_model():
                print_error("Failed to download Phi-3-Mini model")
                sys.exit(1)
            
            # Test the model
            test_phi3_model()
        else:
            print_warning("Phi-3-Mini model is required for AI summarization")
    
    # Step 5: Check/Install Python dependencies
    missing_packages = check_dependencies()
    if missing_packages:
        response = input(f"\nInstall missing packages? (y/n): ")
        if response.lower() == 'y':
            install_dependencies(missing_packages)
    
    # Step 6: Check/Download Whisper model
    if not check_whisper_model():
        response = input("\nFaster-Whisper model not found. Download now? (y/n): ")
        if response.lower() == 'y':
            download_whisper_model()
    
    # Step 7: Create models directory
    create_models_directory()
    
    # Step 8: Generate summary report
    generate_summary_report()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup interrupted by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
