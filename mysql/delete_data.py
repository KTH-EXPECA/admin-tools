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
        
    one_day_ago = datetime.now() - timedelta(days=1)
    one_day_ago_utc = one_day_ago.astimezone(timezone.utc)
    tablequery = "DELETE FROM " + tablename + " WHERE insertion_time < '" + str(one_day_ago_utc) + "'"

    success = m.delete_data(connection, tablequery)
    if success:
        print("Data from table " + tablename + " in database " + dbname + " was deleted")
    else:
        print("Data from table " + tablename + " in database " + dbname + " could not be deleted")    

    m.close_conn(connection)

    return


if __name__ == "__main__":
    main()
