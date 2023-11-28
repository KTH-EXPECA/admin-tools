import mysql.connector

# MySQL connection configuration
config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',  # Change this if your MySQL server is on a different host
    'port': 3306,         # Change the port if required
}


def list_dbs(config):
    # Establishing connection to MySQL
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Execute the query to list databases
        dbquery = "SHOW DATABASES"
        cursor.execute(dbquery)

        print("MySQL Databases:")
        # Fetch all databases and print each one
        for db in cursor:
            print(db[0])

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)

    finally:
        if 'connection' in locals() or 'connection' in globals():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")


list_dbs(config)


