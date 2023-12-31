import mysqlmod as m
import os
import sys


os.chdir(sys.path[0])            # Set current directory to script directory


def main():
    # MySQL connection configuration
    config, error = m.read_mysql_config('config.json')
    if error:
        print("Config could not be read")
        print(error)
        return

    connection, error = m.open_conn(config)
    if error:
        print(" Connection could not be opened")
        return
    
    dblist, error = m.read_db_list(connection)
    if error:
        print("DB list could not be read")
    else:
        print("Databases:")
        for db in dblist:
            print(db)

    error = m.close_conn(connection)

    return


if __name__ == "__main__":
    main()
