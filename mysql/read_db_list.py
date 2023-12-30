import mysqlmod as m
import os
import sys


os.chdir(sys.path[0])            # Set current directory to script directory


def main():
    # MySQL connection configuration
    success, config = m.read_mysql_config('config.json')
    if not success:
        print("Config could not be read")
        return

    success, connection = m.open_conn(config)
    if not success:
        print(" Connection could not be opened")
        return
    
    success, dblist = m.read_db_list(connection)
    if success:
        print("Databases:")
        for db in dblist:
            print(db)
    else:
        print("DB list could not be read")

    m.close_conn(connection)

    return


if __name__ == "__main__":
    main()
