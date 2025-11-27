"""
Llama Inference Engine for Phi-3-Mini
Uses llama-cpp-python for efficient GGUF model inference
"""
from llama_cpp import Llama
from dataclasses import dataclass
from typing import Optional
import os
import logging
import time


@dataclass
class InferenceConfig:
    """Inference configuration for Phi-3-Mini"""
    # Model path
    model_path: str = "models/phi3-therapy-q4_k_m.gguf"
    
    # Model parameters
    n_ctx: int = 2048  # Context window
    n_threads: int = 4  # CPU threads
    n_gpu_layers: int = 0  # GPU layers (0 for CPU-only)
    
    # Generation parameters
    max_tokens: int = 150
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    
    # Performance
    timeout: int = 45  # seconds
    use_mlock: bool = True
    use_mmap: bool = True
    
    # Resource limits
    max_memory_gb: float = 4.0


class LlamaInferenceEngine:
    """Load and run Phi-3-Mini model for inference"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.model = None
        self.logger = logging.getLogger(__name__)
        
    def load_model(self) -> Llama:
        """Load GGUF model using llama-cpp-python"""
        if not os.path.exists(self.config.model_path):
            raise FileNotFoundError(f"Model file not found: {self.config.model_path}")
        
        self.logger.info(f"🔄 Loading model from {self.config.model_path}")
        start_time = time.time()
        
        try:
            self.model = Llama(
                model_path=self.config.model_path,
                n_ctx=self.config.n_ctx,
                n_threads=self.config.n_threads,
                n_gpu_layers=self.config.n_gpu_layers,
                use_mlock=self.config.use_mlock,
                use_mmap=self.config.use_mmap,
                verbose=False
            )
            
            load_time = time.time() - start_time
            model_size_mb = os.path.getsize(self.config.model_path) / (1024 * 1024)
            
            self.logger.info(f"✅ Model loaded in {load_time:.2f}s ({model_size_mb:.1f}MB)")
            print(f"✅ Phi-3-Mini model loaded ({model_size_mb:.1f}MB)")
            
            return self.model
            
        except Exception as e:
            self.logger.error(f"❌ Model loading failed: {e}")
            raise RuntimeError(f"Failed to load model: {e}")
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None, 
                 temperature: Optional[float] = None, 
                 top_p: Optional[float] = None) -> str:
        """Generate text with specified parameters"""
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        # Use config defaults if not specified
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature
        top_p = top_p or self.config.top_p
        
        input_length = len(prompt)
        self.logger.info(f"🤖 Generating (input: {input_length} chars, max_tokens: {max_tokens})")
        
        start_time = time.time()
        
        try:
            response = self.model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=self.config.top_k,
                repeat_penalty=self.config.repeat_penalty,
                stop=["<|end|>", "<|endoftext|>"],
                echo=False
            )
            
            inference_time = time.time() - start_time
            output_text = response['choices'][0]['text'].strip()
            output_length = len(output_text)
            
            self.logger.info(f"✅ Generated {output_length} chars in {inference_time:.2f}s")
            
            return output_text
            
        except Exception as e:
            self.logger.error(f"❌ Generation failed: {e}")
            raise RuntimeError(f"Text generation failed: {e}")
    
    def generate_with_timeout(self, prompt: str, timeout: Optional[int] = None) -> str:
        """Generate text with timeout handling"""
        import signal
        
        timeout = timeout or self.config.timeout
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Generation exceeded {timeout}s timeout")
        
        # Set timeout (Unix-like systems only)
        if hasattr(signal, 'SIGALRM'):
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        
        try:
            result = self.generate(prompt)
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)  # Cancel alarm
            return result
        except TimeoutError as e:
            self.logger.warning(f"⏱️  Generation timeout: {e}")
            raise
        except Exception as e:
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            raise
    
    def unload_model(self):
        """Unload model from memory"""
        if self.model is not None:
            del self.model
            self.model = None
            self.logger.info("🗑️  Model unloaded")
    
    def get_model_info(self) -> dict:
        """Get model information"""
        if not os.path.exists(self.config.model_path):
            return {"loaded": False, "error": "Model file not found"}
        
        model_size_mb = os.path.getsize(self.config.model_path) / (1024 * 1024)
        
        return {
            "loaded": self.model is not None,
            "model_path": self.config.model_path,
            "model_size_mb": round(model_size_mb, 1),
            "n_ctx": self.config.n_ctx,
            "n_threads": self.config.n_threads,
            "n_gpu_layers": self.config.n_gpu_layers
        }


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


if __name__ == "__main__":
    # Test inference engine
    config = InferenceConfig(
        model_path="models/phi3-therapy-q4_k_m.gguf",
        n_threads=4,
        max_tokens=100
    )
    
    engine = LlamaInferenceEngine(config)
    
    try:
        engine.load_model()
        
        test_prompt = """<|system|>
You are a helpful assistant.<|end|>
<|user|>
What is 2+2?<|end|>
<|assistant|>
"""
        
        response = engine.generate(test_prompt, max_tokens=50)
        print(f"\n🤖 Response: {response}")
        
        info = engine.get_model_info()
        print(f"\n📊 Model Info: {info}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
