from transformers import pipeline
import pandas as pd
from typing import Dict, Any, Union
import numpy as np

class AIAnalyzer:
    def __init__(self):
        # Initialize a simpler sentiment analyzer for demo purposes
        self.text_classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    
    def analyze(self, data: Union[pd.DataFrame, list]) -> Dict[str, Any]:
        """
        Perform AI-powered analysis on the data
        """
        # Convert list back to DataFrame if needed
        if isinstance(data, list):
            data = pd.DataFrame(data)
        
        results = {
            "classifications": self._classify_data(data),
            "anomalies": self._detect_anomalies(data),
            "insights": self._generate_insights(data)
        }
        
        return results
    
    def _classify_data(self, data: pd.DataFrame):
        """Classify the status of measurements"""
        # Analyze text data from notes
        sample_notes = data['notes'].head(5).tolist()
        classifications = self.text_classifier(sample_notes)
        
        # Convert to serializable format
        return {
            "text_sentiment": [
                {"label": c["label"], "score": float(c["score"])}  # Convert numpy float to Python float
                for c in classifications
            ],
            "status_distribution": data['status'].value_counts().to_dict()
        }
    
    def _detect_anomalies(self, data: pd.DataFrame):
        """Detect anomalies in numerical measurements"""
        anomalies = {
            "temperature": self._find_anomalies(data['temperature']),
            "humidity": self._find_anomalies(data['humidity']),
            "pressure": self._find_anomalies(data['pressure'])
        }
        return anomalies
    
    def _generate_insights(self, data: pd.DataFrame):
        """Generate basic insights from the data"""
        # Convert the groupby result to a more JSON-friendly format
        device_summary = []
        for (device, status), count in data.groupby('device_id')['status'].value_counts().items():
            device_summary.append({
                "device_id": device,
                "status": status,
                "count": int(count)  # Convert numpy.int64 to native int
            })

        return {
            "total_records": int(len(data)),
            "time_range": {
                "start": data['timestamp'].min(),
                "end": data['timestamp'].max()
            },
            "critical_events": int(len(data[data['status'] == 'critical'])),
            "device_summary": device_summary
        }
    
    def _find_anomalies(self, series: pd.Series):
        """Simple anomaly detection using z-score"""
        z_scores = np.abs((series - series.mean()) / series.std())
        anomalies = series[z_scores > 3]
        return {
            "count": int(len(anomalies)),  # Convert numpy int to Python int
            "values": {
                str(k): float(v)  # Convert indices and values to native Python types
                for k, v in anomalies.head(5).items()
            }
        } 