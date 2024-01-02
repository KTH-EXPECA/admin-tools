"""A module to read data from a MySQL table.

A module to read data from a MySQL table.
It serves as a way to handle a MySQL database, and to give guidance for how the "mysql.connector" module
and the "mysqlmod" module can be used.
"""

import mysql.connector
import json
import mysqlmod as m
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
        readquery = "SELECT * FROM " + tablename      
        rows = m.read_data(connection, readquery)
        print("Fetched data from MySQL table:")
        for row in rows:
            print(row)

    return


if __name__ == "__main__":
    main()



