"""A module to delete data from a MySQL table.

A module to delete data from a MySQL table.
It serves as a way to handle a MySQL database, and to give guidance for how the "mysql.connector" module
and the "mysqlmod" module can be used.
"""

import mysql.connector
import json
import mysqlmod as m
from datetime import datetime, timezone, timedelta
import os
import sys


os.chdir(sys.path[0])            # Set current directory to script directory


def main():

    dbname = 'expeca'
    tablename = 'dummy_table'
    
    with open('config.json', 'r') as f:
        config = json.load(f)

    config['database'] = dbname

    with mysql.connector.connect(**config) as connection:       
        one_day_ago = datetime.now() - timedelta(days=1)
        one_day_ago_utc = one_day_ago.astimezone(timezone.utc)
        tablequery = "DELETE FROM " + tablename + " WHERE insertion_time < '" + str(one_day_ago_utc) + "'"

        m.delete_data(connection, tablequery)
        print("Data from table " + tablename + " in database " + dbname + " was deleted")

    return


if __name__ == "__main__":
    main()
