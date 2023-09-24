# main.py (FastAPI application)

import os
import random
import pymysql
import pandas as pd
import mysql.connector
from fastapi import FastAPI, UploadFile,File,HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Mysql123",
    "database": "details",
}
# Create a function to read data from an Excel file and store it in MySQL
def employe_excel_file_to_mysql(excel_file, sheet_name):
    # Read data from the remote Excel file into a DataFrame
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    print(df)

    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Drop the table if it exists
    drop_table_query = f"DROP TABLE IF EXISTS employeDetails"
    cursor.execute(drop_table_query)

    # Create a MySQL table if it doesn't exist
    create_table_query = f"CREATE TABLE employeDetails ("
    create_table_query += "Employee_ID INT, Employee_Name VARCHAR(255),used int)"
    cursor.execute(create_table_query)
    connection.commit()

    # Insert data from the DataFrame into the MySQL table
    for _, row in df.iterrows():
        insert_query = f"INSERT INTO employeDetails (Employee_ID, Employee_Name, used) VALUES (%s, %s,0)"
        cursor.execute(insert_query, (int(row['Employee ID']), row['Employee Name']))
        connection.commit()

    # Close the database connection
    connection.close()

@app.post("/uploadfile/")
async def upload_file(file: UploadFile=File(...)):
    # Read the file content
    excel_file = file.file.read()
    #print(excel_file)
    employe_excel_file_to_mysql(excel_file, sheet_name)

    return {"filename": file.filename}

# Usage example
sheet_name = 'Sheet1'
#table_name = 'employeDetails'
#excel_url='input.xlsx'
#excel_file_to_mysql(excel_url, sheet_name, table_name)

# Create a function to read data from an Prize Excel file and store it in MySQL
def prize_excel_file_to_mysql(excel_file, sheet_name):
    # Read data from the remote Excel file into a DataFrame
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    print(df)

    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Drop the table if it exists
    drop_table_query = f"DROP TABLE IF EXISTS prizeDetails"
    cursor.execute(drop_table_query)

    # Create a MySQL table if it doesn't exist
    create_table_query = f"CREATE TABLE prizeDetails ("
    create_table_query += "Prize_ID INT, Prize_Name VARCHAR(255))"
    cursor.execute(create_table_query)
    connection.commit()

    # Insert data from the DataFrame into the MySQL table
    for _, row in df.iterrows():
        insert_query = f"INSERT INTO prizeDetails (Prize_ID, Prize_Name) VALUES (%s, %s)"
        cursor.execute(insert_query, (int(row['Prize ID']), row['Prize Name']))
        connection.commit()

    # Close the database connection
    connection.close()

@app.post("/uploadfilePrize/")
async def upload_file_prize(file: UploadFile=File(...)):
    # Read the file content
    excel_file = file.file.read()
    #print(excel_file)
    prize_excel_file_to_mysql(excel_file, sheet_name)

    return {"filename": file.filename}



# Usage example
sheet_name = 'Sheet1'
#table_name = 'prizeDetails'
#excel_url='input.xlsx'
#excel_file_to_mysql(excel_url, sheet_name, table_name)

# Define a function to fetch a random employee ID from the database
def get_random_employee_id():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            
            cursor.execute("SELECT Employee_ID FROM employedetails WHERE used = 0")
            employee_ids = [list(row) for row in cursor.fetchall()]
            if not employee_ids:
                # If all IDs have been used, reset them to unused
                cursor.execute("UPDATE employedetails SET used = 0")
                connection.commit()
                cursor.execute("SELECT Employee_ID FROM employedetails WHERE used = 0")
                employee_ids = [list(row) for row in cursor.fetchall()]
            random_id = random.choice(employee_ids)
            # Mark the ID as used by updating the 'used' flag to 1
            cursor.execute("UPDATE employedetails SET used = 1 WHERE Employee_ID = %s", random_id)
            connection.commit()
            return random_id
    except Exception as e:
        print(f"Error fetching random employee ID: {e}")
    #finally:
        #connection.close()

# Define an API route to fetch random employee data from the backend
@app.get("/get_random_employee")
def get_random_employee():
    employee_id = get_random_employee_id()
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM employedetails WHERE Employee_ID = %s", employee_id)
            employee_data = cursor.fetchone()
            if employee_data:
                # You can customize this response based on your database schema
                return {"employee_id": employee_data[0], "employee_name": employee_data[1]}
            else:
                return {"message": "Employee not found"}
    except Exception as e:
        print(f"Error fetching employee data: {e}")
    #finally:
        #connection.close()


# Define an API route to fetch Prize Name from the DB
@app.get("/get_prize_name/")
async def get_data_by_id(item_id: int):
    print(item_id)
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT Prize_Name FROM prizedetails WHERE Prize_ID=%s", (item_id))
            prize_name = cursor.fetchone()
            print(prize_name)
            if prize_name:
                # You can customize this response based on your database schema
                return prize_name
            
            else:
                return {"message": "Prize Name not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/get_prize_number/")
async def get_prize_numbber():
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM prizedetails")
            total_prize=cursor.fetchone()[0]
            print(total_prize)
        return total_prize
    except Exception as e:
         raise {"message": "Total Prize not found"}