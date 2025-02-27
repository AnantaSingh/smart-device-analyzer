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
from sklearn.ensemble import IsolationForest
from collections import deque
import joblib
import asyncio
import websockets

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
        self.server = None
        self.loop = None
        self.websocket = None
        self.history = deque(maxlen=100)
        self.anomaly_detector = IsolationForest(contamination=0.15, random_state=42)
        self.is_model_trained = False
        self.port = 5001

    def analyze_sentiment_with_ml(self, metrics):
        """Use ML to analyze device sentiment based on patterns"""
        self.history.append([metrics['cpu_usage'], metrics['memory_usage']])
        
        # Make sentiment more dynamic based on both CPU and Memory
        combined_load = (metrics['cpu_usage'] * 0.7) + (metrics['memory_usage'] * 0.3)
        
        if len(self.history) >= 20 and not self.is_model_trained:
            self.anomaly_detector.fit(list(self.history))
            self.is_model_trained = True
            print("ML Model trained with historical data")

        if self.is_model_trained:
            current_data = [[metrics['cpu_usage'], metrics['memory_usage']]]
            prediction = self.anomaly_detector.predict(current_data)[0]
            
            # More dynamic sentiment analysis
            if prediction == -1:  # Anomaly detected
                if combined_load > 85:
                    return 'Critical'
                return 'Stressed'
            else:
                if combined_load > 70:
                    return 'Fatigued'
                if combined_load > 50:
                    return 'Normal'
                return 'Normal'
        else:
            return self.analyze_sentiment_basic(metrics)

    def analyze_sentiment_basic(self, metrics):
        """Basic rule-based sentiment analysis"""
        combined_load = (metrics['cpu_usage'] * 0.7) + (metrics['memory_usage'] * 0.3)
        
        if combined_load > 85:
            return 'Critical'
        elif combined_load > 70:
            return 'Stressed'
        elif combined_load > 50:
            return 'Fatigued'
        return 'Normal'

    def simulate_device_metrics(self):
        """Simulate more realistic device metrics with patterns"""
        time_of_day = datetime.now().hour
        
        # More variable load simulation
        if np.random.random() < 0.2:  # 20% chance of high load
            cpu_usage = np.random.uniform(70, 100)
            memory_usage = np.random.uniform(60, 90)
        else:
            # Normal operation
            cpu_usage = np.random.uniform(30, 85)
            memory_usage = np.random.uniform(40, 75)
        
        # Add random spikes
        if np.random.random() < 0.1:  # 10% chance of spike
            cpu_usage = min(cpu_usage * 1.5, 100)
            memory_usage = min(memory_usage * 1.3, 100)
        
        return {
            'cpu_usage': round(cpu_usage, 2),
            'memory_usage': round(memory_usage, 2),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def start_server(self, port=5001):
        try:
            import websockets
            import asyncio
            
            async def handler(websocket):
                print(f"New client connected!")
                self.websocket = websocket
                try:
                    while self.running:
                        metrics = self.simulate_device_metrics()
                        sentiment = self.analyze_sentiment_with_ml(metrics)
                        combined_load = round((metrics['cpu_usage'] * 0.7) + (metrics['memory_usage'] * 0.3), 2)
                        
                        data = {
                            **metrics,
                            'sentiment': sentiment,
                            'combined_load': combined_load,
                            'ml_enabled': self.is_model_trained
                        }
                        print(f"Sending data: {data}")
                        await websocket.send(json.dumps(data))
                        await asyncio.sleep(2)
                except websockets.exceptions.ConnectionClosed:
                    print("Client disconnected")
                except Exception as e:
                    print(f"Error in handler: {e}")
                finally:
                    self.websocket = None
                    print("Handler finished")

            async def start_server_async():
                try:
                    self.server = await websockets.serve(
                        handler, 
                        "0.0.0.0", 
                        port,
                        reuse_address=True,
                        close_timeout=1
                    )
                    print(f"WebSocket server running on port {port}")
                    await self.server.wait_closed()
                except Exception as e:
                    print(f"Error in start_server_async: {e}")
                    self.running = False
                    raise

            # Create new event loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.running = True
            
            try:
                self.loop.run_until_complete(start_server_async())
            except Exception as e:
                print(f"Error in event loop: {e}")
                self.stop()
                raise
            
        except Exception as e:
            print(f"Error starting server: {e}")
            self.stop()
            raise

    def stop(self):
        print("Stopping server...")
        self.running = False

        try:
            if self.server:
                self.server.close()
            
            if self.loop and self.loop.is_running():
                async def cleanup():
                    if self.server:
                        await self.server.wait_closed()
                    for task in asyncio.all_tasks(self.loop):
                        task.cancel()
                        try:
                            await task
                        except asyncio.CancelledError:
                            pass

                try:
                    self.loop.run_until_complete(cleanup())
                except Exception as e:
                    print(f"Error during cleanup: {e}")
                finally:
                    self.loop.stop()
                    self.loop.close()

            # Reset all attributes
            self.server = None
            self.loop = None
            self.websocket = None
            
            print("Server stopped successfully")
        except Exception as e:
            print(f"Error during stop: {e}")

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('localhost', 5001))
        print("Connected to server. Receiving data...")
        
        while True:
            data = json.loads(client.recv(1024).decode())
            print("\n" + "="*50)
            print(f"Timestamp: {data['timestamp']}")
            print(f"CPU Usage: {data['cpu_usage']}%")
            print(f"Memory Usage: {data['memory_usage']}%")
            print(f"Combined Load: {data['combined_load']}%")
            print(f"Device Sentiment: {data['sentiment']}")
            
            # Add visual indicators
            if data['sentiment'] == 'Critical':
                print("🔴 CRITICAL STATE - Immediate attention required!")
            elif data['sentiment'] == 'Stressed':
                print("🟠 STRESSED - System under heavy load")
            elif data['sentiment'] == 'Fatigued':
                print("🟡 FATIGUED - Monitor closely")
            else:
                print("🟢 NORMAL - System healthy")
                
            if data['ml_enabled']:
                print("ML Model: Active")
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