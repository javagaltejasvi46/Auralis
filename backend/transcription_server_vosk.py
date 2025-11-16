import asyncio
import websockets
import json
import os
import base64
import tempfile
from vosk import Model, KaldiRecognizer
from audio_processor import convert_to_wav, process_audio_with_vosk

# Load Vosk models
MODELS = {
    'hindi': Model("models/vosk-model-small-hi-0.22"),
    'english': Model("models/vosk-model-small-en-us-0.15")
}

print(f"✅ Loaded models: {', '.join(MODELS.keys())}")
print("🎤 Real-time transcription server starting...")

async def transcribe_audio(websocket):
    """Handle WebSocket connection for real-time transcription"""
    try:
        print(f"🔗 New client connected from {websocket.remote_address}")
        
        # Send welcome message with available languages
        await websocket.send(json.dumps({
            'type': 'connected',
            'message': 'Transcription server ready',
            'languages': list(MODELS.keys())
        }))
        print("📤 Sent welcome message")
        
        # Default language
        current_language = 'hindi'
        recognizer = KaldiRecognizer(MODELS[current_language], 16000)
        recognizer.SetWords(True)
        print(f"✅ Recognizer created for {current_language}")
    except Exception as e:
        print(f"❌ Error in connection setup: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    message_count = 0
    audio_bytes_received = 0
    
    try:
        async for message in websocket:
            message_count += 1
            
            if isinstance(message, bytes):
                audio_bytes_received += len(message)
                print(f"🎵 Received audio chunk #{message_count}: {len(message)} bytes (Total: {audio_bytes_received} bytes)")
                
                # Process audio data
                if recognizer.AcceptWaveform(message):
                    # Final result
                    result = json.loads(recognizer.Result())
                    print(f"📊 Final result: {result}")
                    if result.get('text'):
                        response = json.dumps({
                            'type': 'final',
                            'text': result['text']
                        })
                        await websocket.send(response)
                        print(f"📝 Sent final: {result['text']}")
                else:
                    # Partial result
                    partial = json.loads(recognizer.PartialResult())
                    if partial.get('partial'):
                        response = json.dumps({
                            'type': 'partial',
                            'text': partial['partial']
                        })
                        await websocket.send(response)
                        print(f"⏳ Sent partial: {partial['partial']}")
                        
            elif isinstance(message, str):
                # Handle control messages
                print(f"📨 Received control message (first 100 chars): {message[:100]}...")
                data = json.loads(message)
                
                if data.get('type') == 'set_language':
                    # Change language
                    new_language = data.get('language', 'hindi')
                    if new_language in MODELS:
                        current_language = new_language
                        recognizer = KaldiRecognizer(MODELS[current_language], 16000)
                        recognizer.SetWords(True)
                        print(f"🌍 Language changed to: {current_language}")
                        await websocket.send(json.dumps({
                            'type': 'language_changed',
                            'language': current_language
                        }))
                    else:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': f'Unknown language: {new_language}'
                        }))
                
                elif data.get('type') == 'audio_file':
                    print(f"🎵 Received audio file for transcription (Language: {current_language})")
                    
                    try:
                        # Decode base64 audio
                        audio_data = data.get('data', '')
                        if audio_data.startswith('data:'):
                            # Remove data URL prefix
                            audio_data = audio_data.split(',')[1]
                        
                        audio_bytes = base64.b64decode(audio_data)
                        print(f"📦 Decoded audio: {len(audio_bytes)} bytes")
                        
                        # Save to temp file
                        with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as temp_file:
                            temp_file.write(audio_bytes)
                            temp_m4a_path = temp_file.name
                        
                        print(f"💾 Saved to temp file: {temp_m4a_path}")
                        
                        # Send processing message
                        await websocket.send(json.dumps({
                            'type': 'processing',
                            'message': 'Converting audio format...'
                        }))
                        
                        # Convert to WAV
                        print("🔄 Converting to WAV...")
                        wav_path = convert_to_wav(temp_m4a_path)
                        
                        if wav_path:
                            print(f"✅ Converted to WAV: {wav_path}")
                            
                            # Send processing message
                            await websocket.send(json.dumps({
                                'type': 'processing',
                                'message': f'Transcribing in {current_language}...'
                            }))
                            
                            # Process with Vosk
                            print(f"🎯 Processing with Vosk ({current_language})...")
                            result_text = process_audio_with_vosk(wav_path, MODELS[current_language])
                            
                            if result_text:
                                print(f"✅ Transcription: {result_text}")
                                await websocket.send(json.dumps({
                                    'type': 'final',
                                    'text': result_text,
                                    'language': current_language
                                }))
                            else:
                                print("⚠️ No transcription result")
                                await websocket.send(json.dumps({
                                    'type': 'final',
                                    'text': '(No speech detected)',
                                    'language': current_language
                                }))
                            
                            # Clean up WAV
                            os.unlink(wav_path)
                        else:
                            print("❌ Failed to convert audio")
                            await websocket.send(json.dumps({
                                'type': 'error',
                                'message': 'Failed to convert audio. Please install ffmpeg.'
                            }))
                        
                        # Clean up M4A
                        os.unlink(temp_m4a_path)
                        
                    except Exception as e:
                        print(f"❌ Error processing audio file: {e}")
                        import traceback
                        traceback.print_exc()
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': f'Error processing audio: {str(e)}'
                        }))
                
                elif data.get('type') == 'stop':
                    # Get final result
                    final = json.loads(recognizer.FinalResult())
                    print(f"🏁 Final result on stop: {final}")
                    if final.get('text'):
                        response = json.dumps({
                            'type': 'final',
                            'text': final['text']
                        })
                        await websocket.send(response)
                        print(f"📝 Sent final on stop: {final['text']}")
                    print("⏹️  Recording stopped")
                    
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Client disconnected from {websocket.remote_address}")
        print(f"📊 Stats: {message_count} messages, {audio_bytes_received} bytes received")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"🔌 Connection closed")
        print(f"📊 Final stats: {message_count} messages, {audio_bytes_received} bytes received")

async def main():
    """Start WebSocket server"""
    try:
        server = await websockets.serve(
            transcribe_audio,
            "0.0.0.0",
            8003,
            ping_interval=20,
            ping_timeout=20,
            max_size=10 * 1024 * 1024  # 10MB max message size
        )
        
        print("🚀 Transcription server running on ws://0.0.0.0:8003")
        print("📱 Ready to receive audio streams...")
        print("💡 Waiting for connections... (Press Ctrl+C to stop)")
        
        await server.wait_closed()
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
