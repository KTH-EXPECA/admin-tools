"""A module to create a MySQL table.

A module to create a MySQL table.
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

    dbname = 'expeca'
    tablename = 'dummy_table'
    
    with open('config.json', 'r') as f:
        config = json.load(f)

    config['database'] = dbname

    with mysql.connector.connect(**config) as connection:       
        tablequery =   "CREATE TABLE IF NOT EXISTS " + tablename + "(" + \
                            "id INT AUTO_INCREMENT PRIMARY KEY," + \
                            "username VARCHAR(50) UNIQUE NOT NULL," + \
                            "email VARCHAR(100) UNIQUE NOT NULL," + \
                            "insertion_time DATETIME" + \
                        ")"
        
        m.create_table(connection, tablequery)
        print("Table " + tablename + " in database " + dbname + " was created")

    return


if __name__ == "__main__":
    main()




