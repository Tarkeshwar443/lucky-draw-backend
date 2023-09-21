import pandas as pd
import mysql.connector
from fastapi import FastAPI, UploadFile,File
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define your MySQL database configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mysql123',
    'database': 'employelist',
}

# Create a function to read data from an Excel file and store it in MySQL
def excel_file_to_mysql(excel_file, sheet_name, table_name):
    # Read data from the remote Excel file into a DataFrame
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    print(df)

    # Connect to the MySQL database
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor()

    # Drop the table if it exists
    drop_table_query = f"DROP TABLE IF EXISTS {table_name}"
    cursor.execute(drop_table_query)

    # Create a MySQL table if it doesn't exist
    create_table_query = f"CREATE TABLE {table_name} ("
    create_table_query += "Employee_ID INT, Employee_Name VARCHAR(255))"
    cursor.execute(create_table_query)
    connection.commit()

    # Insert data from the DataFrame into the MySQL table
    for _, row in df.iterrows():
        insert_query = f"INSERT INTO {table_name} (Employee_ID, Employee_Name) VALUES (%s, %s)"
        cursor.execute(insert_query, (int(row['Employee ID']), row['Employee Name']))
        connection.commit()

    # Close the database connection
    connection.close()

@app.post("/uploadfile/")
async def upload_file(file: UploadFile=File(...)):
    # Read the file content
    excel_file = file.file.read()
    #print(excel_file)
    excel_file_to_mysql(excel_file, sheet_name, table_name)

    return {"filename": file.filename}

# Usage example
sheet_name = 'Sheet1'
table_name = 'employeDetails'
#excel_url='input.xlsx'
#excel_file_to_mysql(excel_url, sheet_name, table_name)