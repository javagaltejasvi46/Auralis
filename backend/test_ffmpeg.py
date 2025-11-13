"""Test if FFmpeg is accessible"""
import subprocess
import sys

print("🔍 Testing FFmpeg installation...")

try:
    result = subprocess.run(
        ['ffmpeg', '-version'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        print("✅ FFmpeg is installed and accessible!")
        print("\nVersion info:")
        print(result.stdout.split('\n')[0])
        sys.exit(0)
    else:
        print("❌ FFmpeg command failed")
        print(result.stderr)
        sys.exit(1)
        
except FileNotFoundError:
    print("❌ FFmpeg not found in PATH")
    print("\nPlease install FFmpeg:")
    print("  winget install Gyan.FFmpeg.Essentials")
    print("\nThen restart your terminal and try again.")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error testing FFmpeg: {e}")
    sys.exit(1)
