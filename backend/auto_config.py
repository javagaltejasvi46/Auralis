"""
Auto-configuration script for Auralis
Automatically detects local IP and updates configuration files
Run this on startup or when network changes
"""
import socket
import json
import os
from pathlib import Path

def get_local_ip():
    """Get the local IP address of the machine"""
    try:
        # Create a socket to determine the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to an external address (doesn't actually send data)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"❌ Error getting local IP: {e}")
        return "localhost"

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
        
        # Replace the IP address in API_BASE_URL and WS_BASE_URL
        import re
        # Match pattern like: export const API_BASE_URL = 'http://xxx.xxx.xxx.xxx:8002';
        pattern = r"(export const API_BASE_URL = 'http://)[\d.]+(:8002';)"
        replacement = rf"\g<1>{ip_address}\g<2>"
        new_content = re.sub(pattern, replacement, content)
        
        # Update WS_BASE_URL (WebSocket URL)
        pattern_ws = r"(export const WS_BASE_URL = 'ws://)[\d.]+(:8003';)"
        replacement_ws = rf"\g<1>{ip_address}\g<2>"
        new_content = re.sub(pattern_ws, replacement_ws, new_content)
        
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
