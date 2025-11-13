"""Simple WebSocket test server to verify connection works"""
import asyncio
import websockets
import json

async def echo_handler(websocket, path):
    """Simple echo handler for testing"""
    print(f"✅ Client connected from {websocket.remote_address}")
    print(f"📍 Path: {path}")
    
    try:
        # Send welcome message
        await websocket.send(json.dumps({
            'type': 'welcome',
            'message': 'Test server connected!'
        }))
        print("📤 Sent welcome message")
        
        # Echo messages back
        async for message in websocket:
            print(f"📨 Received: {message[:100]}...")  # Print first 100 chars
            
            if isinstance(message, str):
                data = json.loads(message)
                response = json.dumps({
                    'type': 'echo',
                    'received': data
                })
                await websocket.send(response)
                print(f"📤 Sent echo response")
            elif isinstance(message, bytes):
                print(f"📦 Received {len(message)} bytes of binary data")
                await websocket.send(json.dumps({
                    'type': 'binary_received',
                    'size': len(message)
                }))
                
    except websockets.exceptions.ConnectionClosed:
        print("❌ Connection closed")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("🔌 Handler finished")

async def main():
    """Start test server"""
    print("🚀 Starting test WebSocket server on ws://0.0.0.0:8001")
    
    server = await websockets.serve(
        echo_handler,
        "0.0.0.0",
        8001,
        ping_interval=20,
        ping_timeout=20
    )
    
    print("✅ Server running! Waiting for connections...")
    print("💡 Press Ctrl+C to stop")
    
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
