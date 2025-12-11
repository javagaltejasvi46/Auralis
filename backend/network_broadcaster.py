"""
Network Broadcaster - Simple UDP broadcast for server discovery
"""
import socket
import json
import threading
import time
from auto_config import get_local_ip

class NetworkBroadcaster:
    def __init__(self, port=8004):
        self.port = port
        self.running = False
        self.thread = None
        self.local_ip = get_local_ip()
        
    def start_broadcasting(self):
        """Start broadcasting server information"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._broadcast_loop, daemon=True)
        self.thread.start()
        print(f"📡 Broadcasting server info on port {self.port}")
        
    def stop_broadcasting(self):
        """Stop broadcasting"""
        self.running = False
        if self.thread:
            self.thread.join()
            
    def _broadcast_loop(self):
        """Main broadcast loop"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        server_info = {
            "service": "auralis",
            "version": "2.0.0",
            "ip": self.local_ip,
            "api_port": 8002,
            "ws_port": 8003,
            "timestamp": int(time.time())
        }
        
        message = json.dumps(server_info).encode('utf-8')
        
        try:
            while self.running:
                try:
                    # Broadcast to common network ranges
                    broadcast_addresses = [
                        '255.255.255.255',  # Global broadcast
                        '192.168.1.255',    # Common home network
                        '192.168.0.255',    # Alternative home network
                        '10.255.255.255',   # Corporate network
                    ]
                    
                    for addr in broadcast_addresses:
                        try:
                            sock.sendto(message, (addr, self.port))
                        except:
                            pass  # Ignore individual broadcast failures
                            
                    time.sleep(2)  # Broadcast every 2 seconds
                except Exception as e:
                    print(f"Broadcast error: {e}")
                    time.sleep(5)
        finally:
            sock.close()

# Global broadcaster instance
broadcaster = NetworkBroadcaster()

def start_broadcaster():
    """Start the network broadcaster"""
    broadcaster.start_broadcasting()

def stop_broadcaster():
    """Stop the network broadcaster"""
    broadcaster.stop_broadcasting()

if __name__ == "__main__":
    # Test the broadcaster
    start_broadcaster()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_broadcaster()