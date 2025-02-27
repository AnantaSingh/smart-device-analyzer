from flask import Flask, render_template, jsonify
from ai_analyzer import DeviceAnalyzer
import threading
import json

app = Flask(__name__)
device_analyzer = DeviceAnalyzer()
analyzer_thread = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_analyzer')
def start_analyzer():
    global analyzer_thread, device_analyzer
    try:
        # Stop any existing analyzer
        if analyzer_thread and analyzer_thread.is_alive():
            device_analyzer.stop()
            analyzer_thread.join(timeout=2)
            
        # Create a new analyzer instance
        device_analyzer = DeviceAnalyzer()
        
        # Start new thread
        analyzer_thread = threading.Thread(target=device_analyzer.start_server)
        analyzer_thread.start()
        print("Analyzer thread started")
        return jsonify({"status": "success", "message": "Analyzer started"})
    except Exception as e:
        print(f"Error in start_analyzer: {e}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/stop_analyzer')
def stop_analyzer():
    global analyzer_thread
    try:
        if analyzer_thread and analyzer_thread.is_alive():
            device_analyzer.stop()
            analyzer_thread.join(timeout=2)
            analyzer_thread = None
            return jsonify({"status": "success", "message": "Analyzer stopped"})
        return jsonify({"status": "success", "message": "Analyzer not running"})
    except Exception as e:
        print(f"Error stopping analyzer: {e}")
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000) 