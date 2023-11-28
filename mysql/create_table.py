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

tablequery =   "CREATE TABLE IF NOT EXISTS " + tablename + "(" + \
                    "id INT AUTO_INCREMENT PRIMARY KEY," + \
                    "username VARCHAR(50) UNIQUE NOT NULL," + \
                    "email VARCHAR(100) UNIQUE NOT NULL" + \
                ")"


def create_table(config, tablequery):
    # Establishing connection to MySQL
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Execute the query to create the table
        cursor.execute(tablequery)
        print("Table created successfully!")

    except mysql.connector.Error as error:
        print("Error while connecting to MySQL", error)

    finally:
        if 'connection' in locals() or 'connection' in globals():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")



create_table(config, tablequery)


