# Smart Device Analyzer

An advanced AI-powered system for analyzing device and sensor data, providing intelligent insights through sentiment analysis and anomaly detection.

## Overview

This project leverages artificial intelligence to:
- Analyze device/sensor data in real-time
- Detect anomalies and potential issues
- Provide sentiment analysis on data patterns
- Generate actionable insights
- Monitor device performance

## Key Features

🔍 **Real-time Analysis**
- Continuous monitoring of device data
- Instant anomaly detection
- Real-time performance metrics

🤖 **AI Capabilities**
- Machine Learning based pattern recognition
- Sentiment analysis of data trends
- Predictive analytics
- Automated insight generation

📊 **Data Processing**
- Efficient data handling
- Scalable architecture
- Robust error handling

## Project Structure

```python
smart-device-analyzer/
├── AIAPP/
│   └── ai_analyzer.py
├── requirements.txt
└── README.md
```

## Technical Requirements

- Python 3.9+
- PyTorch
- Additional dependencies in requirements.txt

## Prerequisites

- Python 3.9+
- pip (Python package installer)
- Terminal or Command Prompt

## Installation & Setup

1. Navigate to project directory:
```bash
cd /Users/anantasingh/Projects/AIApp
```

2. Create and activate virtual environment:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows
```

3. Install required packages:
```bash
pip install numpy
```

## Running the Application

The application uses a client-server architecture and requires two terminal windows.

### Start the Server (Terminal 1):
```bash
# Navigate to src directory
cd /Users/anantasingh/Projects/AIApp/src

# Run the analyzer
python ai_analyzer.py

# Enter 1 when prompted to start server
```

### Start the Client (Terminal 2):
```bash
# Navigate to src directory
cd /Users/anantasingh/Projects/AIApp/src

# Run the analyzer
python ai_analyzer.py

# Enter 2 when prompted to start client
```

### Expected Output

- **Server Terminal:**
  - "Server started on port 5001"
  - Connection status messages

- **Client Terminal:**
  - Real-time device metrics
  - Sentiment analysis results
  - Anomaly detection alerts
  - CPU and Memory usage statistics

### Stopping the Application

- Press `Ctrl+C` in either terminal to stop the respective component
- Close both terminals to completely shut down the application

## Troubleshooting

If you encounter port-in-use errors:
1. Wait a few minutes and try again
2. Check if another instance is running
3. Use Activity Monitor (macOS) or Task Manager (Windows) to check port usage

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.

## Contact

Ananta Singh
- GitHub: [@AnantaSingh](https://github.com/AnantaSingh)
- Project Link: [https://github.com/AnantaSingh/smart-device-analyzer](https://github.com/AnantaSingh/smart-device-analyzer)
