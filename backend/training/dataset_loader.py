"""
Dataset loader for psychotherapy transcription data.
Handles CSV loading, validation, and train/val/test splitting.
"""

import pandas as pd
import logging
from typing import Tuple, Dict
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatasetLoader:
    """Loads and preprocesses psychotherapy transcription dataset."""
    
    def __init__(self, csv_path: str, train_ratio: float = 0.8, val_ratio: float = 0.1, test_ratio: float = 0.1):
        """
        Initialize the dataset loader.
        
        Args:
            csv_path: Path to the CSV file containing transcriptions and summaries
            train_ratio: Proportion of data for training (default: 0.8)
            val_ratio: Proportion of data for validation (default: 0.1)
            test_ratio: Proportion of data for testing (default: 0.1)
        """
        self.csv_path = Path(csv_path)
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        
        # Validate ratios sum to 1.0
        if not abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6:
            raise ValueError(f"Split ratios must sum to 1.0, got {train_ratio + val_ratio + test_ratio}")
        
        self.df = None
        self.train_df = None
        self.val_df = None
        self.test_df = None
    
    def load_csv(self) -> pd.DataFrame:
        """
        Load CSV file with proper encoding handling.
        
        Returns:
            DataFrame with loaded data
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If required columns are missing
        """
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        try:
            # Try UTF-8 first
            self.df = pd.read_csv(self.csv_path, encoding='utf-8')
            logger.info(f"Loaded CSV with UTF-8 encoding: {len(self.df)} records")
        except UnicodeDecodeError:
            # Fallback to latin-1
            logger.warning("UTF-8 decoding failed, trying latin-1 encoding")
            self.df = pd.read_csv(self.csv_path, encoding='latin-1')
            logger.info(f"Loaded CSV with latin-1 encoding: {len(self.df)} records")
        
        # Validate required columns
        self._validate_columns()
        
        return self.df
    
    def _validate_columns(self):
        """
        Validate that required columns exist in the dataset.
        
        Raises:
            ValueError: If required columns are missing
        """
        required_columns = ['session_transcription', 'session_summary']
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {missing_columns}. "
                f"Available columns: {list(self.df.columns)}"
            )
        
        logger.info(f"Validated columns: {list(self.df.columns)}")
    
    def validate_data(self) -> Dict[str, any]:
        """
        Validate data quality and return statistics.
        
        Returns:
            Dictionary with validation statistics
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_csv() first.")
        
        stats = {
            'total_records': len(self.df),
            'missing_transcriptions': self.df['session_transcription'].isnull().sum(),
            'missing_summaries': self.df['session_summary'].isnull().sum(),
            'empty_transcriptions': (self.df['session_transcription'].str.strip() == '').sum(),
            'empty_summaries': (self.df['session_summary'].str.strip() == '').sum(),
            'avg_transcription_length': self.df['session_transcription'].str.len().mean(),
            'avg_summary_length': self.df['session_summary'].str.len().mean(),
        }
        
        # Log warnings for data quality issues
        if stats['missing_transcriptions'] > 0:
            logger.warning(f"Found {stats['missing_transcriptions']} missing transcriptions")
        if stats['missing_summaries'] > 0:
            logger.warning(f"Found {stats['missing_summaries']} missing summaries")
        if stats['empty_transcriptions'] > 0:
            logger.warning(f"Found {stats['empty_transcriptions']} empty transcriptions")
        if stats['empty_summaries'] > 0:
            logger.warning(f"Found {stats['empty_summaries']} empty summaries")
        
        logger.info(f"Data validation complete: {stats}")
        return stats
    
    def split_dataset(self, shuffle: bool = True, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split dataset into train, validation, and test sets.
        
        Args:
            shuffle: Whether to shuffle data before splitting (default: True)
            random_state: Random seed for reproducibility (default: 42)
            
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_csv() first.")
        
        # Remove any rows with missing or empty data
        clean_df = self.df.dropna(subset=['session_transcription', 'session_summary'])
        clean_df = clean_df[
            (clean_df['session_transcription'].str.strip() != '') &
            (clean_df['session_summary'].str.strip() != '')
        ].copy()
        
        if len(clean_df) < len(self.df):
            logger.warning(f"Removed {len(self.df) - len(clean_df)} invalid records")
        
        # Shuffle if requested
        if shuffle:
            clean_df = clean_df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
        
        # Calculate split indices
        n = len(clean_df)
        train_end = int(n * self.train_ratio)
        val_end = train_end + int(n * self.val_ratio)
        
        # Split the data
        self.train_df = clean_df.iloc[:train_end].reset_index(drop=True)
        self.val_df = clean_df.iloc[train_end:val_end].reset_index(drop=True)
        self.test_df = clean_df.iloc[val_end:].reset_index(drop=True)
        
        logger.info(f"Dataset split complete:")
        logger.info(f"  Train: {len(self.train_df)} samples ({len(self.train_df)/n*100:.1f}%)")
        logger.info(f"  Val:   {len(self.val_df)} samples ({len(self.val_df)/n*100:.1f}%)")
        logger.info(f"  Test:  {len(self.test_df)} samples ({len(self.test_df)/n*100:.1f}%)")
        
        return self.train_df, self.val_df, self.test_df
    
    def get_splits(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Get the train, validation, and test splits.
        
        Returns:
            Tuple of (train_df, val_df, test_df)
            
        Raises:
            ValueError: If splits haven't been created yet
        """
        if self.train_df is None or self.val_df is None or self.test_df is None:
            raise ValueError("Splits not created. Call split_dataset() first.")
        
        return self.train_df, self.val_df, self.test_df
    
    def save_splits(self, output_dir: str):
        """
        Save train, validation, and test splits to separate CSV files.
        
        Args:
            output_dir: Directory to save the split files
        """
        if self.train_df is None or self.val_df is None or self.test_df is None:
            raise ValueError("Splits not created. Call split_dataset() first.")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.train_df.to_csv(output_path / 'train.csv', index=False)
        self.val_df.to_csv(output_path / 'val.csv', index=False)
        self.test_df.to_csv(output_path / 'test.csv', index=False)
        
        logger.info(f"Saved splits to {output_path}")


if __name__ == "__main__":
    # Example usage
    loader = DatasetLoader('../../psychotherapy_transcriptions_100.csv')
    
    # Load and validate
    df = loader.load_csv()
    stats = loader.validate_data()
    
    # Split dataset
    train_df, val_df, test_df = loader.split_dataset()
    
    # Save splits
    loader.save_splits('../models/data_splits')
    
    print("\nDataset loading complete!")
    print(f"Train: {len(train_df)} samples")
    print(f"Val: {len(val_df)} samples")
    print(f"Test: {len(test_df)} samples")
