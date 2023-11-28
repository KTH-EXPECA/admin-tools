import mysql.connector

dbname = 'test_db'
tablename = 'test_table'

# MySQL connection configuration
config = {
    'user': 'root',
    'password': 'peletara',
    'host': 'localhost',  # Change this if your MySQL server is on a different host
    'port': 3306,         # Change the port if required
    'database': dbname,   # Change this to the specific database
}


def describe_table(config, tablename):
    # Establishing connection to MySQL
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Execute the query to describe the table
        tablequery = "DESCRIBE " + tablename
        cursor.execute(tablequery)
        for description in cursor:
            print(description)

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)

    finally:
        if 'connection' in locals() or 'connection' in globals():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")



describe_table(config, tablename)


