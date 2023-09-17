import pandas as pd
import mysql.connector

# Define your MySQL database configuration
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Mysql123',
    'database': 'employelist',
}
# Remote URL of the Excel file
excel_url = 'https://example.com/your_remote_excel_file.xlsx'

# Create a function to read data from a remote Excel file and store it in MySQL
def excel_from_url_to_mysql(excel_url, sheet_name, table_name):
    # Read data from the remote Excel file into a DataFrame
    df = pd.read_excel(excel_url, sheet_name=sheet_name)

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

# Usage example
sheet_name = 'Sheet1'
table_name = 'details'

excel_from_url_to_mysql(excel_url, sheet_name, table_name)