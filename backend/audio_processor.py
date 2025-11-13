"""Audio processing utilities for transcription"""
import subprocess
import tempfile
import os
import wave

def convert_to_wav(input_path, output_path=None, sample_rate=16000):
    """
    Convert audio file to WAV format suitable for Vosk
    Requires ffmpeg to be installed
    """
    if output_path is None:
        output_path = tempfile.mktemp(suffix='.wav')
    
    try:
        # Find ffmpeg executable
        import shutil
        ffmpeg_path = shutil.which('ffmpeg')
        
        if not ffmpeg_path:
            # Try common installation paths
            possible_paths = [
                r"C:\Users\tejasvi javagal\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe",
                r"C:\ffmpeg\bin\ffmpeg.exe",
                r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    ffmpeg_path = path
                    break
        
        if not ffmpeg_path:
            print("❌ FFmpeg not found in PATH or common locations")
            return None
        
        print(f"🔧 Using FFmpeg: {ffmpeg_path}")
        
        # Use ffmpeg to convert
        cmd = [
            ffmpeg_path,
            '-i', input_path,
            '-ar', str(sample_rate),  # Sample rate
            '-ac', '1',  # Mono
            '-f', 'wav',  # Output format
            '-y',  # Overwrite
            '-loglevel', 'error',  # Only show errors
            output_path
        ]
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            shell=False
        )
        
        print(f"📊 FFmpeg return code: {result.returncode}")
        
        if result.returncode == 0:
            print(f"✅ Conversion successful: {output_path}")
            if os.path.exists(output_path):
                print(f"📁 Output file size: {os.path.getsize(output_path)} bytes")
                return output_path
            else:
                print("❌ Output file not created")
                return None
        else:
            print(f"❌ FFmpeg error (code {result.returncode}): {result.stderr}")
            if result.stdout:
                print(f"FFmpeg stdout: {result.stdout}")
            return None
            
    except FileNotFoundError as e:
        print(f"❌ FFmpeg not found: {e}")
        print("Windows: Download from https://ffmpeg.org/download.html")
        print("Or use: winget install ffmpeg")
        print("Make sure to restart your terminal after installation")
        return None
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg conversion timed out (>30 seconds)")
        return None
    except Exception as e:
        print(f"❌ Error converting audio: {e}")
        import traceback
        traceback.print_exc()
        return None

def process_audio_with_vosk(wav_path, model, sample_rate=16000):
    """
    Process WAV file with Vosk and return transcription
    """
    from vosk import KaldiRecognizer
    
    try:
        wf = wave.open(wav_path, "rb")
        
        # Verify format
        if wf.getnchannels() != 1:
            print("❌ Audio must be mono")
            return None
        if wf.getsampwidth() != 2:
            print("❌ Audio must be 16-bit")
            return None
        if wf.getframerate() != sample_rate:
            print(f"⚠️ Sample rate is {wf.getframerate()}, expected {sample_rate}")
        
        # Create recognizer
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        
        # Process audio
        results = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            
            if rec.AcceptWaveform(data):
                import json
                result = json.loads(rec.Result())
                if result.get('text'):
                    results.append(result['text'])
        
        # Get final result
        import json
        final_result = json.loads(rec.FinalResult())
        if final_result.get('text'):
            results.append(final_result['text'])
        
        wf.close()
        
        # Combine all results
        full_text = ' '.join(results)
        return full_text if full_text else None
        
    except Exception as e:
        print(f"❌ Error processing with Vosk: {e}")
        import traceback
        traceback.print_exc()
        return None
