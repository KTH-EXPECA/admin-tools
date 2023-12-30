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
    
    tablequery =   "CREATE TABLE IF NOT EXISTS " + tablename + "(" + \
                        "id INT AUTO_INCREMENT PRIMARY KEY," + \
                        "username VARCHAR(50) UNIQUE NOT NULL," + \
                        "email VARCHAR(100) UNIQUE NOT NULL," + \
                        "insertion_time DATETIME" + \
                    ")"
    
    success = m.create_table(connection, tablequery)

    if success:
        print("Table " + tablename + " in database " + dbname + " was created")
    else:
        print("Table " + tablename + " in database " + dbname + " could not be created")

    m.close_conn(connection)

    return


if __name__ == "__main__":
    main()




