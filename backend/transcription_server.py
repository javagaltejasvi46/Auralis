import asyncio
import websockets
import json
import os
import base64
import tempfile
from faster_whisper import WhisperModel
import subprocess

# Fix OpenMP library conflict
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

# Load Faster-Whisper medium model (better for Hindi Devanagari)
print("🔄 Loading Faster-Whisper medium model...")
model = WhisperModel("medium", device="cpu", compute_type="int8")
print("✅ Faster-Whisper model loaded successfully")
print("💡 Medium model provides native Devanagari output for Hindi")

# Language mapping
LANGUAGE_MAP = {
    'hindi': 'hi',
    'english': 'en'
}

print("🎤 Real-time transcription server starting...")

def transcribe_audio_file(audio_path, language='en'):
    """Transcribe audio file using Faster-Whisper"""
    try:
        print(f"🎯 Transcribing with Faster-Whisper (language: {language})...")
        
        # Transcribe with Faster-Whisper
        # Medium model natively outputs Devanagari for Hindi
        segments, info = model.transcribe(
            audio_path,
            language=language if language != 'auto' else None,  # Let Whisper detect if auto
            beam_size=5,
            vad_filter=False,  # Disable VAD to avoid onnxruntime dependency
            task='transcribe',  # Use transcribe (not translate) to preserve native script
            condition_on_previous_text=False  # Better for short audio clips
        )
        
        # Collect all segments
        text = " ".join([segment.text for segment in segments])
        result = text.strip()
        
        print(f"📝 Transcription: {result}")
        print(f"📊 Detected language: {info.language}, probability: {info.language_probability:.2f}")
        
        return result
    except Exception as e:
        print(f"❌ Faster-Whisper transcription error: {e}")
        import traceback
        traceback.print_exc()
        return None

def convert_audio_to_wav(input_path):
    """Convert audio to WAV format using ffmpeg"""
    try:
        print(f"🔄 Converting audio to WAV format with ffmpeg...")
        output_path = input_path.rsplit('.', 1)[0] + '_converted.wav'
        
        # Use ffmpeg to convert
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-ar', '16000',  # 16kHz sample rate
            '-ac', '1',      # Mono
            '-y',            # Overwrite output
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"✅ Converted to WAV: {output_path}")
            return output_path
        else:
            print(f"❌ FFmpeg conversion failed: {result.stderr}")
            return None
    except Exception as e:
        print(f"❌ Audio conversion error: {e}")
        import traceback
        traceback.print_exc()
        return None

async def transcribe_audio(websocket):
    """Handle WebSocket connection for real-time transcription"""
    try:
        print(f"🔗 New client connected from {websocket.remote_address}")
        
        # Send welcome message with available languages
        await websocket.send(json.dumps({
            'type': 'connected',
            'message': 'Faster-Whisper transcription server ready',
            'languages': list(LANGUAGE_MAP.keys())
        }))
        print("📤 Sent welcome message")
        
        # Default language
        current_language = 'hindi'
        print(f"✅ Default language set to: {current_language}")
    except Exception as e:
        print(f"❌ Error in connection setup: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    message_count = 0
    audio_buffer = []
    
    try:
        async for message in websocket:
            message_count += 1
            
            if isinstance(message, bytes):
                # Collect audio chunks for batch processing
                audio_buffer.append(message)
                print(f"🎵 Received audio chunk #{message_count}: {len(message)} bytes (Buffer: {len(audio_buffer)} chunks)")
                
                # Process every 10 chunks or when buffer is large enough
                if len(audio_buffer) >= 10:
                    print(f"📦 Processing audio buffer...")
                    
                    # Combine audio chunks
                    combined_audio = b''.join(audio_buffer)
                    audio_buffer = []
                    
                    # Save to temp file
                    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                        temp_file.write(combined_audio)
                        temp_path = temp_file.name
                    
                    try:
                        # Transcribe with Whisper
                        whisper_lang = LANGUAGE_MAP.get(current_language, 'en')
                        result_text = transcribe_audio_file(temp_path, whisper_lang)
                        
                        if result_text:
                            await websocket.send(json.dumps({
                                'type': 'partial',
                                'text': result_text
                            }))
                            print(f"⏳ Sent partial: {result_text}")
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
                        
            elif isinstance(message, str):
                # Handle control messages
                print(f"📨 Received control message: {message[:100]}...")
                data = json.loads(message)
                
                if data.get('type') == 'set_language':
                    # Change language
                    new_language = data.get('language', 'hindi')
                    if new_language in LANGUAGE_MAP:
                        current_language = new_language
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
                        wav_path = convert_audio_to_wav(temp_m4a_path)
                        
                        if wav_path:
                            # Send processing message
                            await websocket.send(json.dumps({
                                'type': 'processing',
                                'message': f'Transcribing with Faster-Whisper ({current_language})...'
                            }))
                            
                            # Transcribe with Whisper
                            whisper_lang = LANGUAGE_MAP.get(current_language, 'en')
                            result_text = transcribe_audio_file(wav_path, whisper_lang)
                            
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
                                'message': 'Failed to convert audio format.'
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
                    # Process any remaining audio in buffer
                    if audio_buffer:
                        print(f"🏁 Processing final audio buffer...")
                        combined_audio = b''.join(audio_buffer)
                        audio_buffer = []
                        
                        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                            temp_file.write(combined_audio)
                            temp_path = temp_file.name
                        
                        try:
                            whisper_lang = LANGUAGE_MAP.get(current_language, 'en')
                            result_text = transcribe_audio_file(temp_path, whisper_lang)
                            
                            if result_text:
                                await websocket.send(json.dumps({
                                    'type': 'final',
                                    'text': result_text
                                }))
                                print(f"📝 Sent final: {result_text}")
                        finally:
                            if os.path.exists(temp_path):
                                os.unlink(temp_path)
                    
                    print("⏹️  Recording stopped")
                    
    except websockets.exceptions.ConnectionClosed:
        print(f"❌ Client disconnected from {websocket.remote_address}")
        print(f"📊 Stats: {message_count} messages received")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"🔌 Connection closed")
        print(f"📊 Final stats: {message_count} messages")

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
        
        print("🚀 Faster-Whisper transcription server running on ws://0.0.0.0:8003")
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
