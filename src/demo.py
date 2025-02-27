import uvicorn
import requests
import json
from pprint import pprint

def run_demo():
    """Run a demonstration of the data engineering platform"""
    print("Starting Data Engineering Platform Demo...")
    
    try:
        # Make a request to process sample data
        response = requests.post(
            "http://localhost:8000/process-data",
            params={"data_source": "sample"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        
        if response.ok:
            print("\n=== Analysis Results ===")
            pprint(response.json())
        else:
            print(f"Error: Server returned status code {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the server. Make sure it's running on http://localhost:8000")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("1. Start the server in one terminal with: uvicorn src.main:app --reload")
    print("2. Run this demo in another terminal")
    print("\nWould you like to:")
    print("1. Start the server")
    print("2. Run the demo")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
    elif choice == "2":
        run_demo() 