import mysqlmod as m
import os
import sys


os.chdir(sys.path[0])            # Set current directory to script directory


def main():

    dbname = 'dummy_db'

    # MySQL connection configuration
    config, error = m.read_mysql_config('config.json')
    if error:
        print("Config could not be read")
        return

    connection, error = m.open_conn(config, dbname)
    if error:
        print(" Connection could not be opened")
        return
    
    table_list, error = m.read_table_list(connection)
    if error:
        print("Tables from database " + dbname + " could not be read")
    else:
        for table in table_list:
            print(table)

    error = m.close_conn(connection)
    
    return


if __name__ == "__main__":
    main()







