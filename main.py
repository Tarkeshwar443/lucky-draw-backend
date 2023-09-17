# main.py (FastAPI application)

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve the frontend files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Define an API route to fetch data from the backend
@app.get("/get_data_from_backend")
def get_data_from_backend():
    # Query your MySQL database and return the data
    # Replace this with your database query logic
    data = {"message": "Data from MySQL database"}
    return data
