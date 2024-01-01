import mysql.connector
import json
import mysqlmod as m
import os
import sys


os.chdir(sys.path[0])            # Set current directory to script directory


def main():

    with open('config.json', 'r') as f:
        config = json.load(f)

    with mysql.connector.connect(**config) as connection:       
        dblist = m.read_db_list(connection)
        print("Databases:")
        for db in dblist:
            print(db)

    return


if __name__ == "__main__":
    main()
