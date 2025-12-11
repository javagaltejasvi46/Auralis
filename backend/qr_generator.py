"""
QR Code Generator for Server Connection
Generates QR codes containing server connection information
"""
import qrcode
import json
from io import BytesIO
import base64
from auto_config import get_local_ip

def generate_connection_qr():
    """Generate QR code with server connection info"""
    local_ip = get_local_ip()
    
    connection_info = {
        "service": "auralis",
        "ip": local_ip,
        "api_url": f"http://{local_ip}:8002",
        "ws_url": f"ws://{local_ip}:8003",
        "version": "2.0.0"
    }
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(json.dumps(connection_info))
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for web display
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return {
        "qr_data": json.dumps(connection_info),
        "qr_image_base64": img_str,
        "connection_info": connection_info
    }

def print_connection_info():
    """Print connection information to console"""
    local_ip = get_local_ip()
    
    print("\n" + "="*60)
    print("📱 MOBILE APP CONNECTION INFO")
    print("="*60)
    print(f"🌐 Server IP: {local_ip}")
    print(f"🔗 API URL: http://{local_ip}:8002")
    print(f"🎤 WebSocket: ws://{local_ip}:8003")
    print("\n📋 Manual Setup:")
    print(f"   1. Open Auralis mobile app")
    print(f"   2. Tap connection status")
    print(f"   3. Enter IP: {local_ip}")
    print(f"   4. Tap 'Connect'")
    print("="*60 + "\n")

if __name__ == "__main__":
    # Test QR generation
    result = generate_connection_qr()
    print("QR Code generated successfully!")
    print("Connection info:", result["connection_info"])
    print_connection_info()