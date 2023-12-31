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
    
    error = m.delete_table(connection, tablename)
    if error:
        print("Table " + tablename + " in database " + dbname + " could not be deleted")    
    else:
        print("Table " + tablename + " in database " + dbname + " was deleted")

    error = m.close_conn(connection)

    return


if __name__ == "__main__":
    main()





