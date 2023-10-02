import pandas as pd
import mysql.connector
from mysql.connector import Error

# Define your MySQL database connection settings
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Mysql123",
    "database": "details",
}

# Read the CSV file
csv_file = "dummy.csv"  # Replace with the path to your CSV file
df = pd.read_csv(csv_file)
print(df)

# Function to check if a row exists in the database
def row_exists(cursor, row_data):
    query = "SELECT COUNT(*) FROM your_table WHERE id = %s"
    cursor.execute(query, (row_data["id"],))
    count = cursor.fetchone()[0]
    return count > 0

try:
    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Iterate through each row in the CSV
    for index, row in df.iterrows():
        if not row_exists(cursor, row):
            # Row doesn't exist, insert it
            insert_query = """
            INSERT INTO employeeDetails (id, EmpID, ip, datetime, cardtype, type, EmpName)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (row["id"], row["empid"], row["ip"], row["datetime"], row["cardtype"], row["type"], row["empname"]))

    # Commit the changes to the database
    connection.commit()

except Error as e:
    print(f"Error: {e}")

finally:
    # Close the database connection
    if connection.is_connected():
        cursor.close()
        connection.close()
