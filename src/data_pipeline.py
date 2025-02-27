import pandas as pd
from typing import Dict, Any
import logging
import time
from data_handlers.sample_data import generate_sample_data

class DataPipeline:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            "processed_records": 0,
            "processing_time": 0,
            "error_rate": 0
        }
    
    def process(self, data_source: str) -> pd.DataFrame:
        """
        Main pipeline processing function
        """
        try:
            # Load data
            data = self._load_data(data_source)
            
            # Clean and transform
            cleaned_data = self._clean_data(data)
            
            # Validate
            self._validate_data(cleaned_data)
            
            # Update metrics
            self.metrics["processed_records"] = len(cleaned_data)
            
            return cleaned_data
            
        except Exception as e:
            self.logger.error(f"Pipeline error: {str(e)}")
            raise
    
    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics
    
    def _load_data(self, source: str) -> pd.DataFrame:
        """Load data from various sources"""
        if source == "sample":
            data = generate_sample_data()
            # Convert DataFrame to dict for JSON serialization
            return data
        else:
            # You can add more data source handlers here
            raise ValueError(f"Unsupported data source: {source}")
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the data"""
        # Remove any rows with missing values
        cleaned = data.dropna()
        
        # Convert timestamps to datetime if they aren't already
        cleaned['timestamp'] = pd.to_datetime(cleaned['timestamp'])
        
        # Add some derived features
        cleaned['hour'] = cleaned['timestamp'].dt.hour
        cleaned['is_warning'] = cleaned['status'].isin(['warning', 'critical'])
        
        # Convert timestamps to string for JSON serialization
        cleaned['timestamp'] = cleaned['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return cleaned
    
    def _validate_data(self, data: pd.DataFrame) -> bool:
        """Validate the processed data"""
        required_columns = ['timestamp', 'temperature', 'humidity', 'status']
        if not all(col in data.columns for col in required_columns):
            raise ValueError("Missing required columns")
        
        # Validate value ranges
        if not (data['temperature'].between(-50, 50).all()):
            raise ValueError("Temperature values out of expected range")
        
        if not (data['humidity'].between(0, 100).all()):
            raise ValueError("Humidity values out of expected range")
        
        return True 