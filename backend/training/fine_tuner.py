"""
Fine-tuner for Phi-3-Mini model using LoRA and 4-bit quantization.
"""

import torch
import logging
from pathlib import Path
from typing import Optional
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FineTuner:
    """Fine-tunes Phi-3-Mini model for therapy session summarization."""
    
    def __init__(
        self,
        model_name: str = "microsoft/Phi-3-mini-4k-instruct",
        output_dir: str = "./models/phi3-therapy-finetuned",
        use_4bit: bool = True,
    ):
        """
        Initialize the fine-tuner.
        
        Args:
            model_name: Hugging Face model name
            output_dir: Directory to save fine-tuned model
            use_4bit: Whether to use 4-bit quantization
        """
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.use_4bit = use_4bit
        
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
        # Check for GPU availability
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")
        
        if self.device == "cpu":
            logger.warning("No GPU detected. Training will be very slow on CPU.")
    
    def load_tokenizer(self):
        """
        Load and configure the tokenizer.
        
        Returns:
            Configured tokenizer
        """
        logger.info(f"Loading tokenizer: {self.model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True,
            padding_side="right",  # Required for training
        )
        
        # Set padding token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            logger.info(f"Set pad_token to eos_token: {self.tokenizer.eos_token}")
        
        # Add special tokens if needed
        special_tokens = {
            "additional_special_tokens": ["<|system|>", "<|user|>", "<|assistant|>", "<|end|>"]
        }
        num_added = self.tokenizer.add_special_tokens(special_tokens)
        logger.info(f"Added {num_added} special tokens")
        
        logger.info("Tokenizer loaded successfully")
        return self.tokenizer
    
    def load_model(self):
        """
        Load and configure the model with 4-bit quantization.
        
        Returns:
            Loaded model
        """
        logger.info(f"Loading model: {self.model_name}")
        
        # Configure 4-bit quantization
        if self.use_4bit:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",  # Normal Float 4-bit
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,  # Nested quantization
            )
            logger.info("Using 4-bit quantization (NF4)")
        else:
            bnb_config = None
            logger.info("Loading model without quantization")
        
        try:
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                quantization_config=bnb_config,
                device_map="auto" if self.device == "cuda" else None,
                trust_remote_code=True,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )
            
            # Resize token embeddings if we added special tokens
            if self.tokenizer and len(self.tokenizer) > self.model.config.vocab_size:
                self.model.resize_token_embeddings(len(self.tokenizer))
                logger.info(f"Resized token embeddings to {len(self.tokenizer)}")
            
            logger.info("Model loaded successfully")
            
            # Print model info
            total_params = sum(p.numel() for p in self.model.parameters())
            trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
            logger.info(f"Total parameters: {total_params:,}")
            logger.info(f"Trainable parameters: {trainable_params:,}")
            
            return self.model
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def setup_lora(
        self,
        lora_rank: int = 8,
        lora_alpha: int = 16,
        lora_dropout: float = 0.05,
        target_modules: Optional[list] = None,
    ):
        """
        Configure LoRA (Low-Rank Adaptation) for efficient fine-tuning.
        
        Args:
            lora_rank: Rank of LoRA matrices (default: 8)
            lora_alpha: LoRA scaling factor (default: 16)
            lora_dropout: Dropout probability (default: 0.05)
            target_modules: Modules to apply LoRA to (default: Phi-3 specific)
        """
        if self.model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        logger.info("Setting up LoRA configuration")
        
        # Phi-3 specific target modules
        if target_modules is None:
            target_modules = [
                "qkv_proj",    # Query, Key, Value projection
                "o_proj",      # Output projection
                "gate_up_proj", # Gate and Up projection (MLP)
                "down_proj",   # Down projection (MLP)
            ]
        
        # Configure LoRA
        lora_config = LoraConfig(
            r=lora_rank,
            lora_alpha=lora_alpha,
            target_modules=target_modules,
            lora_dropout=lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
        )
        
        logger.info(f"LoRA config: rank={lora_rank}, alpha={lora_alpha}, dropout={lora_dropout}")
        logger.info(f"Target modules: {target_modules}")
        
        # Prepare model for k-bit training
        if self.use_4bit:
            self.model = prepare_model_for_kbit_training(self.model)
            logger.info("Prepared model for k-bit training")
        
        # Apply LoRA
        self.model = get_peft_model(self.model, lora_config)
        
        # Enable gradient checkpointing for memory efficiency
        self.model.gradient_checkpointing_enable()
        logger.info("Enabled gradient checkpointing")
        
        # Print trainable parameters
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_percentage = 100 * trainable_params / total_params
        
        logger.info(f"Trainable parameters after LoRA: {trainable_params:,} ({trainable_percentage:.2f}%)")
        
        return self.model
    
    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        if self.model is None:
            return {"error": "Model not loaded"}
        
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        return {
            "model_name": self.model_name,
            "device": self.device,
            "use_4bit": self.use_4bit,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "trainable_percentage": 100 * trainable_params / total_params,
        }


if __name__ == "__main__":
    # Example usage
    logger.info("Initializing FineTuner...")
    
    fine_tuner = FineTuner(
        model_name="microsoft/Phi-3-mini-4k-instruct",
        output_dir="./models/phi3-therapy-finetuned",
        use_4bit=True,
    )
    
    # Load tokenizer
    tokenizer = fine_tuner.load_tokenizer()
    logger.info(f"Tokenizer vocabulary size: {len(tokenizer)}")
    
    # Load model
    model = fine_tuner.load_model()
    
    # Setup LoRA
    model = fine_tuner.setup_lora(
        lora_rank=8,
        lora_alpha=16,
        lora_dropout=0.05,
    )
    
    # Print model info
    info = fine_tuner.get_model_info()
    logger.info("Model Information:")
    for key, value in info.items():
        if isinstance(value, float):
            logger.info(f"  {key}: {value:.2f}")
        else:
            logger.info(f"  {key}: {value}")
    
    logger.info("\nModel and tokenizer setup complete!")
