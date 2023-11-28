import mysql.connector

dbname = 'test_db'

# MySQL connection configuration
config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',  # Change this if your MySQL server is on a different host
    'port': 3306,         # Change the port if required
}


def delete_db(config, dbname):
    # Establishing connection to MySQL
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Execute the query to create the database
        dbquery = "DROP DATABASE IF EXISTS " + dbname
        cursor.execute(dbquery)
        print("Database deleted successfully!")

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)

    finally:
        if 'connection' in locals() or 'connection' in globals():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


delete_db(config, dbname)


