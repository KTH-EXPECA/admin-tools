import mysqlmod as m
import os
import sys


os.chdir(sys.path[0])            # Set current directory to script directory


def main():

    dbname = 'dummy_db'
    tablename = 'dummy_table'
    
    # MySQL connection configuration
    success, config = m.read_mysql_config('config.json')
    if not success:
        print("Config could not be read")
        return

    success, connection = m.open_conn(config, dbname)
    if not success:
        print(" Connection could not be opened")
        return
    
    readquery = "SELECT * FROM " + tablename
    
    success, rows = m.read_data(connection, readquery)
    if success:
        print("Fetched data from MySQL table:")
        for row in rows:
            print(row)
    else:
        print("Data could not be read from table " + tablename + " in database " + dbname)

    m.close_conn(connection)

    return


if __name__ == "__main__":
    main()



