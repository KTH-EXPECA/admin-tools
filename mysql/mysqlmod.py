
def read_db_list(connection):
    """Takes a MySQL connection as input and returns a list of MySQL database names (strings)."""
    dblist = []

    with connection.cursor() as cursor:
        dbquery = "SHOW DATABASES"
        cursor.execute(dbquery)
        for db in cursor:
            dblist.append(db[0])

    return dblist


def create_db(connection, dbname):
    """Takes a MySQL connection plus database name as input and creates the database."""
    with connection.cursor() as cursor:
        dbquery = "CREATE DATABASE IF NOT EXISTS " + dbname
        cursor.execute(dbquery)

    return


def delete_db(connection, dbname):
    """Takes a MySQL connection plus database name as input and deletes the database."""
    with connection.cursor() as cursor:
        dbquery = "DROP DATABASE IF EXISTS " + dbname
        cursor.execute(dbquery)

    return


def read_table_list(connection):
    """Takes a MySQL connection (including database) as input and returns a list of table names (strings)."""
    table_list = []
    
    with connection.cursor() as cursor:
        tablequery = "SHOW TABLES"
        cursor.execute(tablequery)
        for table in cursor:
            table_list.append(table[0])
        
    return table_list


def describe_table(connection, tablename):
    """Takes in a MySQL connection (including database) as input and returns a list of table descriptions (tuples)."""
    descr_list = []

    with connection.cursor() as cursor:
        tablequery = "DESCRIBE " + tablename
        cursor.execute(tablequery)
        for description in cursor:
            descr_list.append(description)

    return descr_list


def create_table(connection, tablequery):
    """Takes in a MySQL connection (including database) plus a table-creation query string as input and creates a table."""
    with connection.cursor() as cursor:
        cursor.execute(tablequery)

    return


def delete_table(connection, tablename):
    """Takes in a MySQL connection (including database) plus a table name as input and deletes the table."""
    with connection.cursor() as cursor:
        tablequery = "DROP TABLE IF EXISTS " + tablename
        cursor.execute(tablequery)

    return


def read_data(connection, readquery):
    """Takes in a MySQL connection (including database) plus a data-reading query string as input and returns a list of data rows (tuples)."""
    rows = []

    with connection.cursor() as cursor:
        cursor.execute(readquery)
        rows = cursor.fetchall()

    return rows


def insert_data(connection, tablename, datalist):
    """Takes in a MySQL connection (including database), a table name, and a dictionary of data (fieldname: value) as input, and inserts the data into the table."""
    with connection.cursor() as cursor:
        for data in datalist:
            # Construct the SQL query
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            insertquery = f"INSERT INTO {tablename} ({columns}) VALUES ({placeholders})"
            # Execute the query
            cursor.execute(insertquery, list(data.values()))

        connection.commit()

    return


def delete_data(connection, tablequery):
    """Takes in a MySQL connection (including database) plus a data-deletion query string as input and deletes data from a table."""
    with connection.cursor() as cursor:
        cursor.execute(tablequery)
        connection.commit()

    return

