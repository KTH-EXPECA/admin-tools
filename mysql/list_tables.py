import mysql.connector

dbname = 'test_db'

# MySQL connection configuration
config = {
    'user': 'root',
    'password': 'peletara',
    'host': 'localhost',  # Change this if your MySQL server is on a different host
    'port': 3306,         # Change the port if required
    'database': dbname,   # Change this to the specific database
}


def list_tables(config):
    # Establishing connection to MySQL
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Execute the query to list tables
        tablequery = "SHOW TABLES"
        cursor.execute(tablequery)
        for table in cursor:
            print(table[0])

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)

    finally:
        if 'connection' in locals() or 'connection' in globals():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")



list_tables(config)


