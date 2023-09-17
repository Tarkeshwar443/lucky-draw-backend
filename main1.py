# main.py (FastAPI application)

import os
import random
import pymysql
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# # Determine the path to the 'frontend' directory
# frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

# # Serve the frontend files
# app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Mysql123",
    "database": "employelist",
}

# Define a function to fetch a random employee ID from the database
def get_random_employee_id():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM participants")
            employee_ids = [list(row) for row in cursor.fetchall()]
            print("All employee ids ", employee_ids[1][0])
            return random.choice(employee_ids)
    except Exception as e:
        print(f"Error fetching random employee ID: {e}")
    # finally:
    #     connection.close()

# Define an API route to fetch random employee data from the backend
@app.get("/get_random_employee")
def get_random_employee():
    employee_id = get_random_employee_id()
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM participants WHERE id = %s", employee_id)
            employee_data = cursor.fetchone()
            print(employee_data)
            if employee_data:
                # You can customize this response based on your database schema
                return {"employee_id": employee_data[1], "employee_name": employee_data[0]}
            else:
                return {"message": "Employee not found"}
    except Exception as e:
        print(f"Error fetching employee data: {e}")
    # finally:
    #     connection.close()
