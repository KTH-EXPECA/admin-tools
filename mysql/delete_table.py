import mysql.connector

dbname = 'test_db'
tablename = 'test_table'

# MySQL connection configuration
config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',  # Change this if your MySQL server is on a different host
    'port': 3306,         # Change the port if required
    'database': dbname,   # Change this to the specific database
}


def delete_table(config, tablename):
    # Establishing connection to MySQL
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Execute the query to delete the table
        tablequery = "DROP TABLE IF EXISTS " + tablename
        cursor.execute(tablequery)
        print("Table deleted successfully!")

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)

    finally:
        if 'connection' in locals() or 'connection' in globals():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")



delete_table(config, tablename)


