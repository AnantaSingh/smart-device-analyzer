from fastapi import FastAPI
from data_pipeline import DataPipeline
from ai_analyzer import AIAnalyzer
from config import settings
import pandas as pd

app = FastAPI(title="Data Engineering Platform")
pipeline = DataPipeline()
analyzer = AIAnalyzer()

@app.get("/")
async def root():
    return {"message": "Data Engineering Platform API"}

@app.post("/process-data")
async def process_data(data_source: str):
    # Process data through the pipeline
    processed_data = pipeline.process(data_source)
    
    # Convert DataFrame to dict for JSON serialization
    if isinstance(processed_data, pd.DataFrame):
        processed_data = processed_data.to_dict(orient='records')
    
    # Get analysis results
    analysis = analyzer.analyze(processed_data)
    
    # Ensure all data is JSON serializable
    response = {
        "status": "success",
        "analysis": analysis,
        "metrics": pipeline.get_metrics()
    }
    
    return response 