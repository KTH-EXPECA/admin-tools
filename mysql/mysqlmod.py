import mysql.connector
import json


# Reads and returns a dictionary from a JSON file
def read_mysql_config(fname):
    config = None
    error = "Undefined error"

    try:
        with open(fname, 'r') as f:
            config = json.load(f)
        error = None
    
    except Exception as e:
        error = str(e)

    return config, error


def open_conn(config, dbname=None):

    tempconfig = config
    if dbname:
        tempconfig['database'] = dbname

    connection = None
    error = "Undefined error"

    # Establishing connection to MySQL
    try:
        connection = mysql.connector.connect(**tempconfig)
        error = None

    except Exception as e:
        error = str(e)

    return connection, error


def close_conn(connection):

    error = "Undefined error"

    try:
        if connection and connection.is_connected():
            connection.close()
        error = None

    except Exception as e:
        error = str(e)

    return error


def read_db_list(connection):

    cursor = None
    dblist = []
    error = "Undefined error"

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to list databases
        dbquery = "SHOW DATABASES"
        cursor.execute(dbquery)

        # Fetch all databases and put in list
        for db in cursor:
            dblist.append(db[0])
        
        error = None

    except Exception as e:
        error = str(e)

    finally:
        if cursor:
            cursor.close()

    return dblist, error


def create_db(connection, dbname):

    cursor = None
    error = "Undefined error"

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to create the database
        dbquery = "CREATE DATABASE IF NOT EXISTS " + dbname
        cursor.execute(dbquery)
        error = None

    except Exception as e:
        error = str(e)

    finally:
        if cursor:
            cursor.close()

    return error


def delete_db(connection, dbname):

    cursor = None
    error = "Undefined error"

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to delete the database
        dbquery = "DROP DATABASE IF EXISTS " + dbname
        cursor.execute(dbquery)
        error = None

    except Exception as e:
        error = str(e)

    finally:
        if cursor:
            cursor.close()

    return error


def read_table_list(connection):

    cursor = None
    table_list = []
    error = "Undefined error"
    
    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to list tables
        tablequery = "SHOW TABLES"
        cursor.execute(tablequery)
        for table in cursor:
            table_list.append(table[0])
        error = None
        
    except Exception as e:
        error = str(e)

    finally:
        if cursor:
            cursor.close()

    return table_list, error


def describe_table(connection, tablename):

    cursor = None
    descr_list = []
    error = "Undefined error"

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to describe the table
        tablequery = "DESCRIBE " + tablename
        cursor.execute(tablequery)
        for description in cursor:
            descr_list.append(description)

        error = None

    except Exception as e:
        error = str(e)

    finally:
        if cursor:
            cursor.close()

    return descr_list, error


def create_table(connection, tablequery):

    cursor = None
    error = "Undefined error"

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to create the table
        cursor.execute(tablequery)
        error = None

    except Exception as e:
        error = str(e)

    finally:
        if cursor:
            cursor.close()

    return error


def delete_table(connection, tablename):

    cursor = None
    error = "Undefined error"

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to delete the table
        tablequery = "DROP TABLE IF EXISTS " + tablename
        cursor.execute(tablequery)
        error = None

    except Exception as e:
        error = str(e)

    finally:
        if cursor:
            cursor.close()

    return error


def read_data(connection, readquery):
    
    cursor = None
    rows = []
    error = "Undefined error"

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Executing the query
        cursor.execute(readquery)

        # Fetching all rows from the table
        rows = cursor.fetchall()

        error = None

    except Exception as e:
        error = str(e)

    finally:
        if cursor:
            cursor.close()

    return rows, error


def insert_data(connection, tablename, datalist):

    cursor = None
    error = "Undefined error"

    # Establishing connection to MySQL
    try:
        # Create a cursor object using the connection
        cursor = connection.cursor()

        for data in datalist:
            # Construct the SQL query
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            insertquery = f"INSERT INTO {tablename} ({columns}) VALUES ({placeholders})"
            # Execute the query
            cursor.execute(insertquery, list(data.values()))

        # Commit the changes
        connection.commit()

        error = None

    except Exception as e:
        error = str(e)

    finally:
        if cursor:
            cursor.close()

    return error


def delete_data(connection, tablequery):

    cursor = None
    error = "Undefined error"

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to delete the table
        cursor.execute(tablequery)
        connection.commit()
        error = None

    except Exception as e:
        error = str(e)

    finally:
        if cursor:
            cursor.close()

    return error

