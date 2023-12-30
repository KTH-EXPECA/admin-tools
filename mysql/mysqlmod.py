import mysql.connector
import json


# Reads and returns a dictionary from a JSON file
def read_mysql_config(fname):
    config = None
    success = False

    try:
        with open(fname, 'r') as f:
            config = json.load(f)
        success = True
    
    except:
        pass

    return success, config


def open_conn(config, dbname=None):

    tempconfig = config
    if dbname:
        tempconfig['database'] = dbname

    connection = None
    success = False
    # Establishing connection to MySQL
    try:
        connection = mysql.connector.connect(**tempconfig)
        success = True

    except:
        pass

    return success, connection


def close_conn(connection):

    if connection and connection.is_connected():
        connection.close()

    return


def read_table_list(connection):

    cursor = None
    table_list = []
    success = False
    
    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to list tables
        tablequery = "SHOW TABLES"
        cursor.execute(tablequery)
        for table in cursor:
            table_list.append(table[0])
        success = True
        
    except:
        pass

    finally:
        if cursor:
            cursor.close()

    return success, table_list



def describe_table(connection, tablename):

    cursor = None
    descr_list = []
    success = False

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to describe the table
        tablequery = "DESCRIBE " + tablename
        cursor.execute(tablequery)
        for description in cursor:
            descr_list.append(description)

        success = True

    except:
        pass

    finally:
        if cursor:
            cursor.close()

    return success, descr_list


def delete_table(connection, tablename):

    cursor = None
    success = False

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to delete the table
        tablequery = "DROP TABLE IF EXISTS " + tablename
        cursor.execute(tablequery)
        success = True

    except:
        pass

    finally:
        if cursor:
            cursor.close()

    return success


def read_data(connection, readquery):
    
    cursor = None
    rows = []
    success = False

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Executing the query
        cursor.execute(readquery)

        # Fetching all rows from the table
        rows = cursor.fetchall()

        success = True

    except :
        pass

    finally:
        if cursor:
            cursor.close()

    return success, rows


def read_db_list(connection):

    cursor = None
    dblist = []
    success = False
    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to list databases
        dbquery = "SHOW DATABASES"
        cursor.execute(dbquery)

        # Fetch all databases and put in list
        for db in cursor:
            dblist.append(db[0])
        
        success = True

    except:
        pass

    finally:
        if cursor:
            cursor.close()

    return success, dblist


def create_db(connection, dbname):

    cursor = None
    success = False

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to create the database
        dbquery = "CREATE DATABASE IF NOT EXISTS " + dbname
        cursor.execute(dbquery)
        success = True

    except:
        pass

    finally:
        if cursor:
            cursor.close()

    return success


def delete_db(connection, dbname):

    cursor = None
    success = False

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to delete the database
        dbquery = "DROP DATABASE IF EXISTS " + dbname
        cursor.execute(dbquery)
        success = True

    except:
        pass

    finally:
        if cursor:
            cursor.close()

    return success


def create_table(connection, tablequery):

    cursor = None
    success = False

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to create the table
        cursor.execute(tablequery)
        success = True

    except:
        pass

    finally:
        if cursor:
            cursor.close()

    return success


def insert_data(connection, tablename, datalist):

    cursor = None
    success = False

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

        success = True

    except:
        pass

    finally:
        if cursor:
            cursor.close()

    return success


def delete_data(connection, tablequery):

    cursor = None
    success = False

    # Establishing connection to MySQL
    try:
        cursor = connection.cursor()

        # Execute the query to delete the table
        cursor.execute(tablequery)
        connection.commit()
        success = True

    except:
        pass

    finally:
        if cursor:
            cursor.close()

    return success

