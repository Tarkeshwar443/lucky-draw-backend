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
# Remote URL of the Excel file
#excel_url = 'input.xlsx'

# Create a function to read data from a remote Excel file and store it in MySQL
def excel_from_url_to_mysql(excel_url, sheet_name, table_name):
    # Read data from the remote Excel file into a DataFrame
    df = pd.read_excel(excel_url, sheet_name=sheet_name)
    print(df)

    # Connect to the MySQL database
    connection = mysql.connector.connect(**mysql_config)
    cursor = connection.cursor()

    # Create a MySQL table if it doesn't exist
    create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ("
    create_table_query += "employee_id INT, employee_name VARCHAR(255))"
    cursor.execute(create_table_query)
    connection.commit()

    # Insert data from the DataFrame into the MySQL table
    for _, row in df.iterrows():
        insert_query = f"INSERT INTO {table_name} (employee_id, employee_name) VALUES (%s, %s)"
        cursor.execute(insert_query, (int(row['Employee ID']), row['Employee Name']))
        connection.commit()

    # Close the database connection
    connection.close()

@app.post("/uploadfile/")
async def upload_file(file: UploadFile=File(...)):
    # Read the file content
    excel_url = file.file.read()
    print(file)
    excel_from_url_to_mysql(excel_url, sheet_name, table_name)
    
    # Process the file content as needed
    # For example, you can save it to disk, parse it, or perform any other operations
    
    # Return a response or do something with the file content
    return {"filename": file.filename}

# Usage example
sheet_name = 'Sheet1'
table_name = 'details'
excel_url='input.xlsx'
excel_from_url_to_mysql(excel_url, sheet_name, table_name)