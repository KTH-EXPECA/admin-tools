import mysqlmod as m
import os
import sys


os.chdir(sys.path[0])            # Set current directory to script directory


def main():

    dbname = 'dummy_db'
    tablename = 'dummy_table'
    
    # MySQL connection configuration
    config, error = m.read_mysql_config('config.json')
    if error:
        print("Config could not be read")
        return

    connection, error = m.open_conn(config, dbname)
    if error:
        print(" Connection could not be opened")
        return
    
    readquery = "SELECT * FROM " + tablename
    
    rows, error = m.read_data(connection, readquery)
    if error:
        print("Data could not be read from table " + tablename + " in database " + dbname)
    else:
        print("Fetched data from MySQL table:")
        for row in rows:
            print(row)

    error = m.close_conn(connection)

    return


if __name__ == "__main__":
    main()



