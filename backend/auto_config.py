"""
Auto-configuration script for Auralis
Automatically detects local IP and updates configuration files
Run this on startup or when network changes
"""
import socket
import json
import os
import subprocess
import platform
from pathlib import Path

def get_local_ip():
    """Get the local IP address of the machine using multiple methods"""
    methods = [
        _get_ip_socket_method,
        _get_ip_hostname_method,
        _get_ip_ifconfig_method,
        _get_ip_ipconfig_method
    ]
    
    for method in methods:
        try:
            ip = method()
            if ip and ip != "127.0.0.1" and ip != "localhost":
                print(f"✅ IP detected using {method.__name__}: {ip}")
                return ip
        except Exception as e:
            print(f"⚠️  {method.__name__} failed: {e}")
            continue
    
    print("❌ All IP detection methods failed, using localhost")
    return "localhost"

def _get_ip_socket_method():
    """Method 1: Socket connection to external address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip

def _get_ip_hostname_method():
    """Method 2: Using hostname resolution"""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

def _get_ip_ifconfig_method():
    """Method 3: Using ifconfig (Linux/Mac)"""
    if platform.system() in ["Linux", "Darwin"]:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'inet ' in line and '127.0.0.1' not in line and 'inet 169.254' not in line:
                parts = line.strip().split()
                for i, part in enumerate(parts):
                    if part == 'inet' and i + 1 < len(parts):
                        ip = parts[i + 1].split('/')[0]  # Remove subnet mask
                        if _is_valid_ip(ip):
                            return ip
    return None

def _get_ip_ipconfig_method():
    """Method 4: Using ipconfig (Windows)"""
    if platform.system() == "Windows":
        result = subprocess.run(['ipconfig'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'IPv4 Address' in line:
                ip = line.split(':')[-1].strip()
                if _is_valid_ip(ip) and not ip.startswith('169.254'):
                    return ip
    return None

def _is_valid_ip(ip):
    """Check if IP address is valid"""
    try:
        parts = ip.split('.')
        return len(parts) == 4 and all(0 <= int(part) <= 255 for part in parts)
    except:
        return False

def update_frontend_config(ip_address):
    """Update frontend config.ts with new IP address"""
    frontend_config_path = Path(__file__).parent.parent / "frontend" / "src" / "config.ts"
    
    if not frontend_config_path.exists():
        print(f"⚠️  Frontend config not found at {frontend_config_path}")
        return False
    
    try:
        # Read the current config
        with open(frontend_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace the IP address in the return statement
        import re
        # Match pattern like: return '192.168.1.100';  // This gets updated automatically by auto_config.py
        pattern = r"(return ')[\d.]+(';\s*//\s*This gets updated automatically by auto_config\.py)"
        replacement = rf"\g<1>{ip_address}\g<2>"
        new_content = re.sub(pattern, replacement, content)
        
        # Write back
        with open(frontend_config_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Frontend config updated: {frontend_config_path}")
        return True
    except Exception as e:
        print(f"❌ Error updating frontend config: {e}")
        return False

def update_backend_config(ip_address):
    """Update backend config.py with new IP address"""
    backend_config_path = Path(__file__).parent / "config.py"
    
    if not backend_config_path.exists():
        print(f"⚠️  Backend config not found at {backend_config_path}")
        return False
    
    try:
        # Read the current config
        with open(backend_config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add or update LOCAL_IP setting
        if "LOCAL_IP:" in content:
            import re
            pattern = r'(LOCAL_IP: str = ")[^"]*(")'
            replacement = rf'\g<1>{ip_address}\g<2>'
            new_content = re.sub(pattern, replacement, content)
        else:
            # Add LOCAL_IP after API_TITLE
            new_content = content.replace(
                'class Settings:',
                f'class Settings:\n    # Network Configuration\n    LOCAL_IP: str = "{ip_address}"'
            )
        
        # Write back
        with open(backend_config_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Backend config updated: {backend_config_path}")
        return True
    except Exception as e:
        print(f"❌ Error updating backend config: {e}")
        return False

def save_ip_cache(ip_address):
    """Save the current IP to a cache file for comparison"""
    cache_file = Path(__file__).parent / ".ip_cache"
    try:
        with open(cache_file, 'w') as f:
            f.write(ip_address)
    except Exception as e:
        print(f"⚠️  Could not save IP cache: {e}")

def get_cached_ip():
    """Get the previously cached IP address"""
    cache_file = Path(__file__).parent / ".ip_cache"
    try:
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return f.read().strip()
    except Exception:
        pass
    return None

def configure_network():
    """Main configuration function"""
    print("\n" + "="*60)
    print("🔧 AURALIS AUTO-CONFIGURATION")
    print("="*60)
    
    # Get current IP
    current_ip = get_local_ip()
    print(f"📡 Detected IP Address: {current_ip}")
    
    # Check if IP has changed
    cached_ip = get_cached_ip()
    if cached_ip == current_ip:
        print(f"✅ IP unchanged ({current_ip}) - No configuration update needed")
        print("="*60 + "\n")
        return current_ip
    
    if cached_ip:
        print(f"🔄 IP changed: {cached_ip} → {current_ip}")
    else:
        print(f"🆕 First time configuration")
    
    # Update configurations
    print("\n📝 Updating configuration files...")
    frontend_success = update_frontend_config(current_ip)
    backend_success = update_backend_config(current_ip)
    
    # Save to cache
    if frontend_success or backend_success:
        save_ip_cache(current_ip)
    
    print("\n" + "="*60)
    if frontend_success and backend_success:
        print("✅ Configuration updated successfully!")
        print(f"🌐 API Base URL: http://{current_ip}:8002")
        print(f"🎤 WebSocket URL: ws://{current_ip}:8003")
    else:
        print("⚠️  Some configurations could not be updated")
    print("="*60 + "\n")
    
    return current_ip

if __name__ == "__main__":
    configure_network()
