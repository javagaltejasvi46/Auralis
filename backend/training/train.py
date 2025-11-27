"""
Training script for fine-tuning Phi-3-Mini on therapy session data.
"""

import os
import sys
import logging
from pathlib import Path
from datasets import Dataset
from transformers import TrainingArguments
from trl import SFTTrainer

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from dataset_loader import DatasetLoader
from text_preprocessor import TextPreprocessor
from prompt_formatter import PromptFormatter
from fine_tuner import FineTuner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def prepare_dataset(csv_path: str, output_dir: str = "../models/data_splits"):
    """
    Load and prepare the dataset.
    
    Args:
        csv_path: Path to CSV file
        output_dir: Directory to save splits
        
    Returns:
        Tuple of (train_dataset, val_dataset, test_dataset)
    """
    logger.info("Loading dataset...")
    loader = DatasetLoader(csv_path)
    
    # Load and validate
    df = loader.load_csv()
    stats = loader.validate_data()
    
    # Split dataset
    train_df, val_df, test_df = loader.split_dataset()
    
    # Save splits
    loader.save_splits(output_dir)
    
    return train_df, val_df, test_df


def format_dataset(df, preprocessor, formatter):
    """
    Format dataset for training.
    
    Args:
        df: DataFrame with transcription and summary columns
        preprocessor: TextPreprocessor instance
        formatter: PromptFormatter instance
        
    Returns:
        Formatted dataset
    """
    logger.info(f"Formatting {len(df)} examples...")
    
    formatted_examples = []
    
    for idx, row in df.iterrows():
        transcription = row['session_transcription']
        summary = row['session_summary']
        
        # Preprocess
        transcription, summary = preprocessor.preprocess_pair(transcription, summary)
        
        # Format prompt
        prompt = formatter.format_single_session(transcription, summary)
        
        formatted_examples.append({"text": prompt})
    
    # Convert to HuggingFace Dataset
    dataset = Dataset.from_dict({"text": [ex["text"] for ex in formatted_examples]})
    
    logger.info(f"Formatted {len(dataset)} examples")
    return dataset


def main():
    """Main training function."""
    
    logger.info("="*50)
    logger.info("Phi-3-Mini Fine-Tuning for Therapy Summarization")
    logger.info("="*50)
    
    # Configuration
    CSV_PATH = "../../psychotherapy_transcriptions_100.csv"
    OUTPUT_DIR = "../models/phi3-therapy-finetuned"
    DATA_SPLITS_DIR = "../models/data_splits"
    
    # Training hyperparameters
    BATCH_SIZE = 1  # Small batch size for 8GB VRAM
    GRADIENT_ACCUMULATION_STEPS = 4  # Effective batch size = 4
    LEARNING_RATE = 2e-4
    NUM_EPOCHS = 3
    MAX_SEQ_LENGTH = 2048
    
    # Step 1: Prepare dataset
    logger.info("\n" + "="*50)
    logger.info("Step 1: Preparing Dataset")
    logger.info("="*50)
    
    train_df, val_df, test_df = prepare_dataset(CSV_PATH, DATA_SPLITS_DIR)
    
    # Step 2: Initialize components
    logger.info("\n" + "="*50)
    logger.info("Step 2: Initializing Components")
    logger.info("="*50)
    
    preprocessor = TextPreprocessor(max_tokens=MAX_SEQ_LENGTH)
    formatter = PromptFormatter()
    fine_tuner = FineTuner(output_dir=OUTPUT_DIR, use_4bit=True)
    
    # Step 3: Load model and tokenizer
    logger.info("\n" + "="*50)
    logger.info("Step 3: Loading Model and Tokenizer")
    logger.info("="*50)
    
    tokenizer = fine_tuner.load_tokenizer()
    model = fine_tuner.load_model()
    
    # Step 4: Setup LoRA
    logger.info("\n" + "="*50)
    logger.info("Step 4: Configuring LoRA")
    logger.info("="*50)
    
    model = fine_tuner.setup_lora(
        lora_rank=8,
        lora_alpha=16,
        lora_dropout=0.05,
    )
    
    # Print model info
    info = fine_tuner.get_model_info()
    logger.info(f"Model: {info['model_name']}")
    logger.info(f"Device: {info['device']}")
    logger.info(f"Total parameters: {info['total_parameters']:,}")
    logger.info(f"Trainable parameters: {info['trainable_parameters']:,} ({info['trainable_percentage']:.2f}%)")
    
    # Step 5: Format datasets
    logger.info("\n" + "="*50)
    logger.info("Step 5: Formatting Datasets")
    logger.info("="*50)
    
    train_dataset = format_dataset(train_df, preprocessor, formatter)
    val_dataset = format_dataset(val_df, preprocessor, formatter)
    
    # Step 6: Configure training
    logger.info("\n" + "="*50)
    logger.info("Step 6: Configuring Training")
    logger.info("="*50)
    
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        logging_steps=10,
        save_steps=50,
        eval_steps=50,
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        warmup_steps=10,
        fp16=True,  # Use mixed precision for faster training
        optim="paged_adamw_8bit",  # Memory-efficient optimizer
        max_grad_norm=0.3,
        report_to="none",  # Disable wandb/tensorboard
    )
    
    logger.info(f"Batch size: {BATCH_SIZE}")
    logger.info(f"Gradient accumulation: {GRADIENT_ACCUMULATION_STEPS}")
    logger.info(f"Effective batch size: {BATCH_SIZE * GRADIENT_ACCUMULATION_STEPS}")
    logger.info(f"Learning rate: {LEARNING_RATE}")
    logger.info(f"Epochs: {NUM_EPOCHS}")
    logger.info(f"Total training steps: ~{len(train_dataset) * NUM_EPOCHS // (BATCH_SIZE * GRADIENT_ACCUMULATION_STEPS)}")
    
    # Step 7: Create trainer
    logger.info("\n" + "="*50)
    logger.info("Step 7: Creating Trainer")
    logger.info("="*50)
    
    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LENGTH,
        packing=False,  # Don't pack multiple examples together
    )
    
    # Step 8: Start training
    logger.info("\n" + "="*50)
    logger.info("Step 8: Starting Training")
    logger.info("="*50)
    logger.info("This will take 2-4 hours on RTX 3050...")
    logger.info("You can monitor GPU usage with: nvidia-smi")
    logger.info("")
    
    try:
        trainer.train()
        
        logger.info("\n" + "="*50)
        logger.info("Training Complete!")
        logger.info("="*50)
        
        # Step 9: Save final model
        logger.info("\n" + "="*50)
        logger.info("Step 9: Saving Model")
        logger.info("="*50)
        
        trainer.save_model(OUTPUT_DIR)
        tokenizer.save_pretrained(OUTPUT_DIR)
        
        logger.info(f"Model saved to: {OUTPUT_DIR}")
        
        # Step 10: Evaluate on test set
        logger.info("\n" + "="*50)
        logger.info("Step 10: Evaluating on Test Set")
        logger.info("="*50)
        
        test_dataset = format_dataset(test_df, preprocessor, formatter)
        test_results = trainer.evaluate(test_dataset)
        
        logger.info("Test Results:")
        for key, value in test_results.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("\n" + "="*50)
        logger.info("All Done!")
        logger.info("="*50)
        logger.info(f"\nYour fine-tuned model is ready at: {OUTPUT_DIR}")
        logger.info("You can now use it for inference!")
        
    except KeyboardInterrupt:
        logger.warning("\n\nTraining interrupted by user")
        logger.info("Saving checkpoint...")
        trainer.save_model(OUTPUT_DIR + "/interrupted")
        logger.info(f"Checkpoint saved to: {OUTPUT_DIR}/interrupted")
        
    except Exception as e:
        logger.error(f"\n\nTraining failed with error: {e}")
        logger.error("Check the error message above for details")
        raise


if __name__ == "__main__":
    main()
