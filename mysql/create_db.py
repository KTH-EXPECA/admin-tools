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

    success, connection = m.open_conn(config)
    if not success:
        print(" Connection could not be opened")
        return
    
    success = m.create_db(connection, dbname)
    if success:
        print("Database " + dbname + " was created")
    else:
        print("Database " + dbname + " could not be created")

    m.close_conn(connection)

    return


if __name__ == "__main__":
    main()



