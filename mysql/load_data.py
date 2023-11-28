import mysql.connector

dbname = 'test_db'
tablename = 'test_table'
data = [
    ("John", "john@example.com"),
    ("Emma", "emma@example.com"),
    ("Michael", "michael@example.com"),
]

# MySQL connection configuration
config = {
    'user': 'root',
    'password': 'peletara',
    'host': 'localhost',  # Change this if your MySQL server is on a different host
    'port': 3306,         # Change the port if required
    'database': dbname,   # Change this to the specific database
}

insertquery = "INSERT INTO " + tablename + " (username, email) VALUES (%s, %s)"


def insert_data(config, insertquery, data):

    # Establishing connection to MySQL
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Execute the query to insert data
        cursor.executemany(insertquery, data)
        connection.commit()
        print(f"{cursor.rowcount} record(s) inserted successfully!")

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)

    finally:
        if 'connection' in locals() or 'connection' in globals():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


insert_data(config, insertquery, data)


