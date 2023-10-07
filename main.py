# main.py (FastAPI application)

import os
import random
import pymysql
import pandas as pd
import mysql.connector
from fastapi import FastAPI, UploadFile,File,HTTPException,Body,Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests
import io
import json

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
                return prize_name[0]
            
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


  # Function to check if a row exists in the database
def row_exists(cursor, row_data):
    query = "SELECT COUNT(*) FROM empDetails WHERE EmpID = %s"
    cursor.execute(query, (row_data["EmpID"],))
    #print(row_data["EmpID"]);
    count = cursor.fetchone()[0]
    return count > 0

@app.get("/update-csv-onsubmit")
async def update_csv_data():
    try:
        # Read the CSV file
        #csv_file = "dummy.csv"  # Replace with the path to your CSV file

         # Make an HTTP GET request to the external API to get the CSV file
        # api_url = "https://example.com/api/get-csv"  # Replace with the actual API URL
        # response = requests.get(api_url)
        
        # if response.status_code != 200:
        #     raise HTTPException(status_code=500, detail="Failed to fetch CSV data from the external API")

        # # Read the CSV content from the API response
        # csv_content = response.text

        # # Parse CSV content into a DataFrame
        # df = pd.read_csv(io.StringIO(csv_content))
        # #df = pd.read_csv(csv_file)
        # print(df)
        # # Connect to the MySQL database
        # connection = mysql.connector.connect(**db_config)
        # cursor = connection.cursor()
        # Read the CSV file
        csv_file = "dummy.csv"  # Replace with the path to your CSV file
        df = pd.read_csv(csv_file)
        print(df)
        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        drop_table_query = "DROP TABLE IF EXISTS EmpDetails"
        cursor.execute(drop_table_query)
        drop_table_query = "DROP TABLE IF EXISTS winnerDetails"
        cursor.execute(drop_table_query)
        create_table_query = """
        CREATE TABLE IF NOT EXISTS EmpDetails (
            EmpID VARCHAR(255) PRIMARY KEY,
            EmpName VARCHAR(255),
            used INT
        )
        """
        cursor.execute(create_table_query)

        create_table_query = """
        CREATE TABLE IF NOT EXISTS winnerDetails (
            serial_number INT PRIMARY KEY,
            EmpID VARCHAR(255),
            EmpName VARCHAR(255),
            prize_name VARCHAR(255)
        )
        """
        cursor.execute(create_table_query)

        # Iterate through each row in the CSV
        for index, row in df.iterrows():
            if not row_exists(cursor, row):
                # Row doesn't exist, insert it
                insert_query = """
                INSERT INTO empDetails (EmpID,EmpName, used)
                VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (row["EmpID"], row["EmpName"], 0 ))
# Commit the changes to the database
        connection.commit()
        return {"message": "CSV data updated in the database"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")



@app.get("/update-csv-onspin")
async def update_csv_data():
    try:
        # Read the CSV file
        csv_file = "dummy.csv"  # Replace with the path to your CSV file
        df = pd.read_csv(csv_file)
        print(df)
        # Connect to the MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Iterate through each row in the CSV
        for index, row in df.iterrows():
            if not row_exists(cursor, row):
                # Row doesn't exist, insert it
                insert_query = """
                INSERT INTO employeDetails (Employee_ID,Employee_Name, used)
                VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (row["EmpID"], row["EmpName"], 0 ))
# Commit the changes to the database
        connection.commit()
        return {"message": "CSV data updated in the database"}

    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # finally:
    #     # Close the database connection
    #     if connection.is_connected():
    #         cursor.close()
    #         connection.close()


 #to store backup data of prize
@app.post("/store_data/")
async def store_data(request:str=Body(...)):
    print(json.loads(request))
    #print(json.loads(request)['serial_number'])
    # print(json.loads(request)['EmpID'])
    # print(json.loads(request)['EmpName'])
    # print(json.loads(request)['prize_name'])
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # Insert data into the database
        insert_query = "INSERT INTO winnerDetails (serial_number,EmpID, EmpName, prize_name) VALUES (%s, %s, %s, %s)"
        data = (json.loads(request)['serial_number'], json.loads(request)['EmpID'], json.loads(request)['EmpName'],json.loads(request)['prize_name'] )
        cursor.execute(insert_query, data)
        # print(cursor)
        # Commit changes and close the connection
        conn.commit()
        #conn.close()
    

        return Response(content="Data stored successfully",status_code=200)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))    


@app.get("/get_data/")
async def get_data():
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Retrieve all data from the database
        select_query = "SELECT * FROM winnerdetails"
        cursor.execute(select_query)

        # Fetch all rows
        data = cursor.fetchall()

        # Close the connection
        conn.close()

        # Convert data to a list of dictionaries for JSON response
        result = [{"serial_number": row[0], "EmpID": row[1], "EmpName": row[2], "prize_name": row[3]} for row in data]

        return result
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))