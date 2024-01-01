import mysql.connector
import json
import mysqlmod as m
from datetime import datetime, timezone, timedelta
import os
import sys


os.chdir(sys.path[0])            # Set current directory to script directory


def main():

    dbname = 'dummy_db'
    tablename = 'dummy_table'
    
    with open('config.json', 'r') as f:
        config = json.load(f)

    config['database'] = dbname

    with mysql.connector.connect(**config) as connection:       
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
        
        m.insert_data(connection, tablename, datalist)
        print("Data was inserted into table " + tablename + " in database " + dbname)

    return


if __name__ == "__main__":
    main()


