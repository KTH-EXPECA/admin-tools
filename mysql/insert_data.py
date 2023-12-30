import mysqlmod as m
from datetime import datetime, timezone, timedelta
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
    
    current_time = datetime.now()
    current_time_utc = current_time.astimezone(timezone.utc)
    datalist = [
        {
            "username"      : "John",
            "email"         : "john@example.com",
            "insertion_time": current_time_utc
        },
        {
            "username"      : "Emma",
            "email"         : "emma@example.com",
            "insertion_time": current_time_utc
        },
        {
            "username"      : "Michael",
            "email"         : "michael@example.com",
            "insertion_time": current_time_utc
        }
    ]
    
    success = m.insert_data(connection, tablename, datalist)
    if success:
        print("Data was inserted into table " + tablename + " in database " + dbname)
    else:
        print("Data could not be inserted into table " + tablename + " in database " + dbname)

    m.close_conn(connection)

    return


if __name__ == "__main__":
    main()


