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
        
    success, descr_list = m.describe_table(connection, tablename)
    if success:
        print("Description of table " + tablename + ":")
        for descr in descr_list:
            print(descr)
    else:
        print("Description of table " + tablename + " in database " + dbname + " could not be read")    

    m.close_conn(connection)

    return


if __name__ == "__main__":
    main()





