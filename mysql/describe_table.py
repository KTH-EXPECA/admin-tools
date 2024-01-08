"""A module to get a description of a MySQL table.

A module to get a description of a MySQL table.
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
        descr_list = m.describe_table(connection, tablename)
        print("Description of table " + tablename + ":")
        for descr in descr_list:
            print(descr)

    return


if __name__ == "__main__":
    main()





