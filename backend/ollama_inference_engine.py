"""
Ollama Inference Engine for Phi-3-Mini
Uses Ollama for simplified local model inference
"""
import requests
import json
import logging
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class OllamaConfig:
    """Ollama inference configuration"""
    # Ollama settings
    base_url: str = "http://localhost:11434"
    model_name: str = "phi3:mini"  # or "phi3:medium", "phi3:3.8b"
    
    # Generation parameters
    max_tokens: int = 150
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    
    # Performance
    timeout: int = 45  # seconds


class OllamaInferenceEngine:
    """Ollama-based inference engine for Phi-3-Mini"""
    
    def __init__(self, config: OllamaConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.model_loaded = False
        
    def check_ollama_running(self) -> bool:
        """Check if Ollama service is running"""
        try:
            response = requests.get(f"{self.config.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def list_models(self) -> list:
        """List available models in Ollama"""
        try:
            response = requests.get(f"{self.config.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            self.logger.error(f"Failed to list models: {e}")
            return []
    
    def pull_model(self, model_name: Optional[str] = None) -> bool:
        """Pull/download model from Ollama registry"""
        model_name = model_name or self.config.model_name
        
        self.logger.info(f"🔄 Pulling model: {model_name}")
        print(f"🔄 Downloading {model_name} from Ollama...")
        print("⏳ This may take a few minutes on first run...")
        
        try:
            response = requests.post(
                f"{self.config.base_url}/api/pull",
                json={"name": model_name},
                stream=True,
                timeout=600  # 10 minutes for download
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get('status', '')
                    if 'pulling' in status.lower():
                        print(f"📥 {status}")
                    elif 'success' in status.lower():
                        print(f"✅ {status}")
                        return True
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to pull model: {e}")
            print(f"❌ Failed to download model: {e}")
            return False
    
    def load_model(self) -> bool:
        """Verify model is available"""
        if not self.check_ollama_running():
            raise RuntimeError(
                "Ollama is not running. Please start Ollama:\n"
                "  Windows: Start Ollama from Start Menu\n"
                "  Mac/Linux: ollama serve"
            )
        
        # Check if model exists
        available_models = self.list_models()
        
        if self.config.model_name not in available_models:
            self.logger.info(f"Model {self.config.model_name} not found, pulling...")
            if not self.pull_model():
                raise RuntimeError(f"Failed to pull model: {self.config.model_name}")
        
        self.model_loaded = True
        print(f"✅ Ollama model ready: {self.config.model_name}")
        return True
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None,
                 temperature: Optional[float] = None,
                 top_p: Optional[float] = None) -> str:
        """Generate text using Ollama"""
        if not self.model_loaded:
            self.load_model()
        
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature
        top_p = top_p or self.config.top_p
        
        self.logger.info(f"🤖 Generating with Ollama (max_tokens: {max_tokens})")
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.config.base_url}/api/generate",
                json={
                    "model": self.config.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,
                        "temperature": temperature,
                        "top_p": top_p,
                        "top_k": self.config.top_k,
                        "stop": ["<|end|>", "<|endoftext|>"]
                    }
                },
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                output_text = data.get('response', '').strip()
                
                inference_time = time.time() - start_time
                self.logger.info(f"✅ Generated {len(output_text)} chars in {inference_time:.2f}s")
                
                return output_text
            else:
                raise RuntimeError(f"Ollama API error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Generation exceeded {self.config.timeout}s timeout")
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            raise RuntimeError(f"Text generation failed: {e}")
    
    def generate_with_timeout(self, prompt: str, timeout: Optional[int] = None) -> str:
        """Generate text with timeout (wrapper for compatibility)"""
        original_timeout = self.config.timeout
        if timeout:
            self.config.timeout = timeout
        
        try:
            result = self.generate(prompt)
            return result
        finally:
            self.config.timeout = original_timeout
    
    def get_model_info(self) -> dict:
        """Get model information"""
        if not self.check_ollama_running():
            return {
                "loaded": False,
                "error": "Ollama not running"
            }
        
        try:
            response = requests.post(
                f"{self.config.base_url}/api/show",
                json={"name": self.config.model_name},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "loaded": self.model_loaded,
                    "model_name": self.config.model_name,
                    "base_url": self.config.base_url,
                    "parameters": data.get('parameters', 'Unknown'),
                    "template": data.get('template', 'Unknown')[:100] + "..."
                }
        except:
            pass
        
        return {
            "loaded": self.model_loaded,
            "model_name": self.config.model_name,
            "base_url": self.config.base_url
        }


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


if __name__ == "__main__":
    # Test Ollama engine
    config = OllamaConfig(
        model_name="phi3:mini",
        max_tokens=100
    )
    
    engine = OllamaInferenceEngine(config)
    
    try:
        # Check if Ollama is running
        if not engine.check_ollama_running():
            print("❌ Ollama is not running!")
            print("Please start Ollama and try again.")
            exit(1)
        
        # Load model
        engine.load_model()
        
        # Test generation
        test_prompt = """<|system|>
You are a helpful assistant.<|end|>
<|user|>
What is 2+2?<|end|>
<|assistant|>
"""
        
        response = engine.generate(test_prompt, max_tokens=50)
        print(f"\n🤖 Response: {response}")
        
        # Get model info
        info = engine.get_model_info()
        print(f"\n📊 Model Info:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
