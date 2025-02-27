from transformers import pipeline
import pandas as pd
from typing import Dict, Any, Union
import numpy as np
from datetime import datetime
import time
import threading
import socket
import json
import warnings

# Suppress the SSL warning
warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')

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

class DeviceAnalyzer:
    def __init__(self):
        self.sentiment_levels = ['Normal', 'Stressed', 'Fatigued', 'Critical']
        self.running = True
        self.server_socket = None
        self.clients = []
        self.port = 5001  # Changed port to 5001

    def analyze_sentiment(self, metrics):
        if metrics['cpu_usage'] > 90:
            return 'Critical'
        elif metrics['cpu_usage'] > 70:
            return 'Stressed'
        elif metrics['cpu_usage'] > 50:
            return 'Fatigued'
        return 'Normal'

    def simulate_device_metrics(self):
        return {
            'cpu_usage': np.random.randint(30, 100),
            'memory_usage': np.random.randint(20, 95),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def start_server(self, port=5001):  # Changed default port to 5001
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Add this line to allow port reuse
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('localhost', port))
            self.server_socket.listen(5)
            print(f"Server started on port {port}")
            
            while self.running:
                try:
                    client, addr = self.server_socket.accept()
                    self.clients.append(client)
                    print(f"Client connected from {addr}")
                    threading.Thread(target=self.handle_client, args=(client,)).start()
                except Exception as e:
                    if self.running:
                        print(f"Error accepting client: {e}")
                    break
        except Exception as e:
            print(f"Error starting server: {e}")
            self.stop()

    def handle_client(self, client):
        while self.running:
            try:
                metrics = self.simulate_device_metrics()
                sentiment = self.analyze_sentiment(metrics)
                data = {**metrics, 'sentiment': sentiment}
                client.send(json.dumps(data).encode())
                time.sleep(2)
            except:
                self.clients.remove(client)
                break

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for client in self.clients:
            client.close()

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('localhost', 5001))  # Changed port to 5001
        print("Connected to server. Receiving data...")
        
        while True:
            data = json.loads(client.recv(1024).decode())
            print("\n" + "="*50)
            print(f"Timestamp: {data['timestamp']}")
            print(f"CPU Usage: {data['cpu_usage']}%")
            print(f"Memory Usage: {data['memory_usage']}%")
            print(f"Device Sentiment: {data['sentiment']}")
            if data['cpu_usage'] > 85:
                print("⚠️ ANOMALY DETECTED!")
            print("="*50)
    except KeyboardInterrupt:
        print("\nClient stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

def main():
    print("\nSmart Device Analyzer")
    print("1. Start Server")
    print("2. Start Client")
    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        analyzer = DeviceAnalyzer()
        try:
            analyzer.start_server()
        except KeyboardInterrupt:
            print("\nServer stopped by user")
            analyzer.stop()
    elif choice == "2":
        start_client()
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main() 