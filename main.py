import uvicorn
from database import load_data_from_csv
import os

if __name__ == "__main__":
    # Load data from CSV into database if database doesn't exist or is empty
    if not os.path.exists("stock_data.db"):
        print("Loading data from CSV into database...")
        load_data_from_csv()
    
    # Start the FastAPI server
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
