"""A module to run a simulation to insert data into a MySQL table, using a sine function.

A module to run a simulation to insert data into a MySQL table, using a sine function.
It serves as a way to handle a MySQL database, and to give guidance for how the "mysql.connector" module
and the "mysqlmod" module can be used.
"""

import mysql.connector
import mysqlmod as m
import time as t
from datetime import datetime, timezone, timedelta
import math
import os
import sys
import keyboard
import json


os.chdir(sys.path[0])            # Set current directory to script directory


def main():

    dbname = 'kth_research'
    tablename = 'test_table'

    with open('config.json', 'r') as f:
        config = json.load(f)

    with mysql.connector.connect(**config) as connection:  
        m.create_db(connection, dbname)

    config['database'] = dbname

    with mysql.connector.connect(**config) as connection:  
        
        tablequery =   "CREATE TABLE IF NOT EXISTS " + tablename + "(" + \
                            "time DATETIME(3)," + \
                            "value DOUBLE," + \
                            "insertion_time DATETIME," + \
                            "PRIMARY KEY(time)" + \
                        ")"
        
        m.create_table(connection, tablequery)
        
        degrees = 1
        key_pressed = False
        print("Simulation is running (press 'b' to interrupt the simulation)")
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

            m.insert_data(connection, tablename, datalist)

            one_day_ago = datetime.now() - timedelta(days=1)
            one_day_ago_utc = one_day_ago.astimezone(timezone.utc)
            tablequery = "DELETE FROM " + tablename + " WHERE insertion_time < '" + str(one_day_ago_utc) + "'"
            
            m.delete_data(connection, tablequery)

            if keyboard.is_pressed('b'):
                key_pressed = True

            t.sleep(1)     # 1 = 1 second between iterations

        print("The simulation was interrupted by pressing 'b'")

    return

if __name__ == "__main__":
    main()
