import mysqlmod as m
import os
import sys


os.chdir(sys.path[0])            # Set current directory to script directory


def main():

    dbname = 'dummy_db'

    # MySQL connection configuration
    success, config = m.read_mysql_config('config.json')
    if not success:
        print("Config could not be read")
        return

    success, connection = m.open_conn(config, dbname)
    if not success:
        print(" Connection could not be opened")
        return
    
    success, table_list = m.read_table_list(connection)
    if success:
        for table in table_list:
            print(table)
    else:
        print("Tables from database " + dbname + " could not be read")

    m.close_conn(connection)
    
    return


if __name__ == "__main__":
    main()







