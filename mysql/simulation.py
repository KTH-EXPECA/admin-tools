import mysqlmod as m
import time as t
from datetime import datetime, timezone, timedelta
import math
import os
import sys
import keyboard


os.chdir(sys.path[0])            # Set current directory to script directory


def main():

    dbname = 'kth_research'
    tablename = 'test_table'

    success, config = m.read_mysql_config('config.json')
    if not success:
        print("Config could not be read")
        return

    success, connection = m.open_conn(config)
    if not success:
        print(" Connection could not be opened")
        return
    
    success = m.create_db(connection, dbname)
    if not success:
        print("Database " + dbname + " could not be created")
        return

    m.close_conn(connection)

    success, connection = m.open_conn(config, dbname)
    if not success:
        print(" Connection could not be opened")
        return
    
    tablequery =   "CREATE TABLE IF NOT EXISTS " + tablename + "(" + \
                        "time DATETIME(3)," + \
                        "value DOUBLE," + \
                        "insertion_time DATETIME," + \
                        "PRIMARY KEY(time)" + \
                    ")"
    
    success = m.create_table(connection, tablequery)
    if not success:
        print("Table " + tablename + " could not be created")
        return
    
    degrees = 1
    key_pressed = False
    print("Simulation is running")
    while not key_pressed:

        local_time = datetime.now()
        time = local_time.astimezone(timezone.utc)
        degrees = degrees + 4
        radians = math.radians(degrees)
        value = math.sin(radians) * 100

        datalist = [
            {
                "time"          : time,
                "value"         : value,
                "insertion_time": time
            }
        ]

        success = m.insert_data(connection, tablename, datalist)
        if not success:
            print("Data at time " + str(time) + " could not be inserted")

        one_day_ago = datetime.now() - timedelta(days=1)
        one_day_ago_utc = one_day_ago.astimezone(timezone.utc)
        tablequery = "DELETE FROM " + tablename + " WHERE insertion_time < '" + str(one_day_ago_utc) + "'"
        
        success = m.delete_data(connection, tablequery)
        if not success:
            print("Data from table " + tablename + " in database " + dbname + " could not be deleted")    

        if keyboard.is_pressed('b'):
            key_pressed = True

        t.sleep(1)     # 1 = 1 second between iterations

    print("The simulation was interrupted by pressing 'b'")

    m.close_conn(connection)

    return

if __name__ == "__main__":
    main()
