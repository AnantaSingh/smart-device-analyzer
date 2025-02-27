import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data(rows=1000):
    """Generate synthetic data for demonstration"""
    np.random.seed(42)
    
    # Generate timestamps
    dates = [datetime.now() - timedelta(minutes=x) for x in range(rows)]
    
    # Generate sample sensor data
    data = {
        'timestamp': dates,
        'temperature': np.random.normal(25, 5, rows),
        'humidity': np.random.normal(60, 10, rows),
        'pressure': np.random.normal(1013, 10, rows),
        'status': np.random.choice(['normal', 'warning', 'critical'], rows),
        'device_id': np.random.choice(['device_' + str(i) for i in range(1, 6)], rows),
        'notes': [f"Measurement from sensor {i % 5 + 1}" for i in range(rows)]
    }
    
    return pd.DataFrame(data) 