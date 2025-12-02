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

# Auto-configure network on startup
from auto_config import configure_network
LOCAL_IP = configure_network()

# Load Faster-Whisper medium model (already downloaded)
print("🔄 Loading Faster-Whisper medium model...")
model = WhisperModel("medium", device="cpu", compute_type="int8")
print("✅ Faster-Whisper model loaded successfully")
print("🌍 Auto-translate mode: All languages → English")
print("💡 Supports Indian languages: Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Punjabi, etc.")
print("👥 Speaker diarization enabled - Identifies different speakers")

print("🎤 Real-time transcription server starting...")

def transcribe_audio_file(audio_path, language=None):
    """Transcribe audio file using Faster-Whisper with 2-speaker diarization (Therapist/Patient)"""
    try:
        print(f"🎯 Transcribing with Faster-Whisper (2-speaker mode: Therapist & Patient)...")
        
        # Auto-detect language and translate to English
        print("🎯 Detecting language and translating to English...")
        
        segments, info = model.transcribe(
            audio_path,
            language=None,  # Auto-detect any language
            beam_size=3,  # Reduced for speed
            vad_filter=False,  # Disable VAD (requires onnxruntime)
            task='translate',  # TRANSLATE to English (not transcribe)
            condition_on_previous_text=False,
            temperature=0.0,
            word_timestamps=True  # For speaker diarization
        )
        
        # Process segments with 2-speaker detection (Therapist & Patient only)
        text_parts = []
        current_speaker = 0  # 0 = Therapist, 1 = Patient (alternating)
        last_end_time = 0
        segment_count = 0
        
        speaker_labels = ["Therapist", "Patient"]
        
        for segment in segments:
            segment_count += 1
            silence_gap = segment.start - last_end_time
            
            # Detect speaker change based on silence gap (>1.5s suggests turn change)
            if silence_gap > 1.5 and last_end_time > 0:
                # Toggle between Therapist (0) and Patient (1)
                current_speaker = 1 - current_speaker
            
            # Add speaker label with text
            speaker_name = speaker_labels[current_speaker]
            text_parts.append(f"{speaker_name}: {segment.text.strip()}")
            
            last_end_time = segment.end
        
        # Join with newlines for clear speaker separation
        result = "\n".join(text_parts)
        
        # If no segments, return empty
        if not result.strip():
            return "(No speech detected)"
        
        print(f"📝 Translation (English): {result[:200]}...")
        print(f"📊 Detected language: {info.language} (confidence: {info.language_probability:.2f})")
        print(f"👥 2-speaker diarization: Therapist & Patient ({segment_count} segments)")
        
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
        
        # Send welcome message
        await websocket.send(json.dumps({
            'type': 'connected',
            'message': 'Faster-Whisper multilingual transcription server ready',
            'mode': 'multilingual',
            'auto_detect': True
        }))
        print("📤 Sent welcome message - Multilingual mode enabled")
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
                        # Transcribe with Whisper (auto-detect language)
                        result_text = transcribe_audio_file(temp_path, None)
                        
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
                
                if data.get('type') == 'audio_file':
                    print(f"🎵 Received audio file for transcription (Multilingual auto-detect)")
                    
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
                                'message': 'Transcribing with Faster-Whisper (Auto-detect)...'
                            }))
                            
                            # Transcribe with Whisper (auto-detect language)
                            result_text = transcribe_audio_file(wav_path, None)
                            
                            if result_text:
                                print(f"✅ Transcription: {result_text}")
                                await websocket.send(json.dumps({
                                    'type': 'final',
                                    'text': result_text,
                                    'mode': 'multilingual'
                                }))
                            else:
                                print("⚠️ No transcription result")
                                await websocket.send(json.dumps({
                                    'type': 'final',
                                    'text': '(No speech detected)',
                                    'mode': 'multilingual'
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
                            result_text = transcribe_audio_file(temp_path, None)
                            
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
