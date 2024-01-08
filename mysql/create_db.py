"""A module to create a MySQL database.

A module to create a MySQL database.
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

    with open('config.json', 'r') as f:
        config = json.load(f)

    with mysql.connector.connect(**config) as connection:         
        m.create_db(connection, dbname)
        print("Database " + dbname + " was created")

    return


if __name__ == "__main__":
    main()



