import os
import requests
import zipfile
from tqdm import tqdm

# Vosk models for multiple languages
MODELS = {
    'hindi': {
        'url': "https://alphacephei.com/vosk/models/vosk-model-small-hi-0.22.zip",
        'name': "vosk-model-small-hi-0.22"
    },
    'english': {
        'url': "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
        'name': "vosk-model-small-en-us-0.15"
    }
}
MODEL_DIR = "models"

def download_file(url, filename):
    """Download file with progress bar"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(filename, 'wb') as file, tqdm(
        desc=filename,
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
    ) as progress_bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            progress_bar.update(size)

def download_model(language):
    """Download a specific language model"""
    if language not in MODELS:
        print(f"❌ Unknown language: {language}")
        print(f"Available: {', '.join(MODELS.keys())}")
        return False
    
    model_info = MODELS[language]
    model_url = model_info['url']
    model_name = model_info['name']
    
    # Create models directory
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    model_path = os.path.join(MODEL_DIR, model_name)
    
    # Check if model already exists
    if os.path.exists(model_path):
        print(f"✅ {language.title()} model already exists at {model_path}")
        return True
    
    # Download model
    zip_path = os.path.join(MODEL_DIR, f"{model_name}.zip")
    
    if not os.path.exists(zip_path):
        print(f"📥 Downloading {language.title()} model from {model_url}...")
        download_file(model_url, zip_path)
        print("✅ Download complete!")
    
    # Extract model
    print(f"📦 Extracting model to {MODEL_DIR}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(MODEL_DIR)
    
    print(f"✅ Model extracted successfully to {model_path}")
    
    # Clean up zip file
    os.remove(zip_path)
    print(f"🎉 {language.title()} model setup complete!")
    return True

def main():
    print("🌍 Vosk Model Downloader")
    print("=" * 50)
    
    # Download all models
    for language in MODELS.keys():
        print(f"\n📥 Setting up {language.title()} model...")
        download_model(language)
    
    print("\n" + "=" * 50)
    print("✅ All models ready!")

if __name__ == "__main__":
    main()
