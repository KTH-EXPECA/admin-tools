import time
import json
import sys
import os
import subprocess as sp
import yaml
from yaml.loader import SafeLoader
from datetime import datetime
import traceback
import mysql.connector
import re


"""
This script is an exporter for MySQL metrics.
It takes metrics from "collector" scripts in JSON format, and pushes them to MySQL.
A config file in YAML format defines the collector scripts (separate Python scripts) and their corresponding metrics,
so that new collectors and/or metrics can be added easily.
Usage: python3 expeca-exporter-influxdb.py &
"""

configfname = "expeca-exporter-mysql.yml"          # YAML file with collector config
eventlogfname = "event.log"      # Output file that will have event message if the script used the "logevent" function
eventlogsize = 3000              # Number of lines allowed in the event log. Oldest lines are cut.

os.chdir(sys.path[0])            # Set current directory to script directory


def logevent(logtext: str, logtext2: Exception = None):
    """
    Writes time stamp plus text or exception info into the event log file.

    If logtext2 is provided (an exception), writes the line number and exception text into the log file.
    If logtext is a regular string, writes the text to the log file.
    If the maximum number of lines is reached, old lines are cut.
    If an exception occurs in this function, it is ignored (pass).
    """
    try:
        # Check if the log file exists and read its content
        if os.path.exists(eventlogfname):
            with open(eventlogfname, "r") as f:
                lines = f.read().splitlines()
            newlines = lines[-eventlogsize:]  # Keep only the most recent lines
        else:
            newlines = []

        # Write the updated content back to the file
        with open(eventlogfname, "w") as f:
            for line in newlines:
                f.write(line + "\n")
            
            now = datetime.now()
            date_time = now.strftime("%Y/%m/%d %H:%M:%S")
            scriptname = os.path.basename(__file__)
            
            # Write the log text (always required)
            log_entry = f"{date_time} {scriptname}: {logtext}"
            
            # If logtext2 (exception) is provided, log the exception details
            if logtext2 is not None:
                if isinstance(logtext2, BaseException):
                    tb = traceback.extract_tb(logtext2.__traceback__)
                    last_traceback = tb[-1]  # Get the most recent traceback entry
                    line_number = last_traceback.lineno
                    exception_message = str(logtext2)
                    log_entry += f" | Exception occurred on line {line_number}: {exception_message}"
            
            f.write(log_entry + "\n")
    except:
        pass

    return


def dict_to_lists(in_dict):
    """Converts a dictionary to a key list and value list"""
    return list(in_dict.keys()), list(in_dict.values())
    # keylist = []
    # valuelist = []
    # for key, value in in_dict.items():
    #     keylist.append(key)
    #     valuelist.append(value)
    # return keylist, valuelist


def seconds_to_next_mark(polling_interval_minutes):
    """Calculates the number of seconds remaining to the next x-minute mark on the clock"""
    now = datetime.now()
    seconds_since_last_mark = (now.minute % polling_interval_minutes) * 60 + now.second
    seconds_to_next_mark = polling_interval_minutes * 60 - seconds_since_last_mark
    return seconds_to_next_mark


def is_valid_identifier(identifier):
    """Checks if a string is a valid SQL identifier."""
    return re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", identifier) is not None

def get_sql_type(py_value):
    """Determines the SQL data type based on the Python data type of the value."""
    import datetime

    # Map of Python types to SQL data types
    type_map = {
        int: "INT",
        float: "FLOAT",
        bool: "BOOLEAN",
        str: "VARCHAR(255)",
        bytes: "BLOB",
        datetime.datetime: "DATETIME",
    }

    # Check the type of py_value and return the corresponding SQL type
    for py_type, sql_type in type_map.items():
        if isinstance(py_value, py_type):
            return sql_type

    # If the type is not supported, raise an error
    raise TypeError(f"Unsupported data type: {type(py_value)}")


def insert_mysql_data(cursor, table_name, labels, value):
    """
    Inserts or updates a record in the MySQL database table specified by 'table_name'.
    If the table does not exist, it is created with a 'value' column whose data type is based on 'value'.
    If columns specified in 'labels' do not exist, they are added to the table with data types based on their values.
    
    Parameters:
    - cursor: MySQL database cursor object.
    - table_name (str): The name of the table to insert or update data in.
    - labels (dict): A dictionary where each key-value pair corresponds to a column name and its value.
    - value: The value to be inserted into the "value" column.
    
    The function checks if a record with the same labels exists.
    - If it exists, it updates the "value" column of that record.
    - If it doesn't exist, it inserts a new record with the given labels and value.
    """
    
    # Ensure table_name is a valid SQL identifier
    if not is_valid_identifier(table_name):
        raise ValueError(f"Invalid table name: {table_name}")
    
    # Ensure label keys are valid SQL identifiers
    for key in labels.keys():
        if not is_valid_identifier(key):
            raise ValueError(f"Invalid column name: {key}")
    
    # Determine SQL data type for the 'value' column based on the 'value' parameter
    value_sql_type = get_sql_type(value)
    
    # Check if the table exists
    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
    table_exists = cursor.fetchone()
    
    if not table_exists:
        # Create the table with 'value' column
        create_table_query = f"""
            CREATE TABLE `{table_name}` (
                `value` {value_sql_type}
            )
        """
        cursor.execute(create_table_query)
    else:
        # Check if 'value' column exists and its data type is compatible
        cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE 'value'")
        value_column_info = cursor.fetchone()
        if not value_column_info:
            # If 'value' column does not exist, add it
            alter_table_query = f"ALTER TABLE `{table_name}` ADD COLUMN `value` {value_sql_type}"
            cursor.execute(alter_table_query)
        else:
            # Optionally, check if existing 'value' column type is compatible with new data type
            existing_value_type = value_column_info[1]  # Data type is in the second column
            # Implement type compatibility checks if necessary
    
    # Fetch existing columns from the table
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
    existing_columns = set(row[0] for row in cursor.fetchall())
    
    # Add columns that do not exist
    for key, val in labels.items():
        if key not in existing_columns:
            label_sql_type = get_sql_type(val)
            alter_query = f"ALTER TABLE `{table_name}` ADD COLUMN `{key}` {label_sql_type}"
            cursor.execute(alter_query)
            existing_columns.add(key)  # Update the set of existing columns
    
    # Build the WHERE clause for the SELECT and UPDATE queries
    where_clauses = []
    where_values = []
    for key, val in labels.items():
        where_clauses.append(f"`{key}` = %s")
        where_values.append(val)
    
    where_clause = " AND ".join(where_clauses) if where_clauses else "1"
    
    # Check if a record with the same labels exists
    select_query = f"SELECT 1 FROM `{table_name}` WHERE {where_clause} LIMIT 1"
    cursor.execute(select_query, where_values)
    exists = cursor.fetchone()
    
    if exists:
        # Update the existing record
        update_query = f"""
            UPDATE `{table_name}` SET
                `value` = %s
            WHERE {where_clause}
        """
        update_values = [value] + where_values
        # logevent("1 " + update_query + " : " + str(update_values))
        cursor.execute(update_query, update_values)
    else:
        # Insert a new record
        columns = ['value'] + list(labels.keys())
        placeholders = ", ".join(["%s"] * len(columns))
        column_names = ", ".join(f"`{col}`" for col in columns)
        insert_query = f"INSERT INTO `{table_name}` ({column_names}) VALUES ({placeholders})"
        insert_values = [value] + list(labels.values())
        # logevent("2 " + insert_query + " : " + str(insert_values))
        cursor.execute(insert_query, insert_values)


def data_retention(cursor, table_list, time_column, retention_days):
    # Validate the time column name
    if not is_valid_identifier(time_column):
        raise ValueError(f"Invalid column name: {time_column}")

    for table in table_list:
        # Validate the table name
        if not is_valid_identifier(table):
            raise ValueError(f"Invalid table name: {table}")

        # Construct the SQL query
        query = f"""
            DELETE FROM `{table}`
            WHERE `{time_column}` < (NOW() - INTERVAL %s DAY)
        """

        try:
            # Execute the query with parameterized retention_days
            cursor.execute(query, (retention_days,))
            # cursor.connection.commit()
        except Exception as e:
            # cursor.connection.rollback()
            # logevent(f"Error processing table {table}: {e}")
            continue  # Proceed to the next table


def datetime_decoder(obj):
    for key, value in obj.items():
        if isinstance(value, str):
            try:
                # Attempt to parse ISO 8601 format
                obj[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                pass  # Not a datetime string, leave it as is
    return obj


def column_exists(cursor, table_name, column_name):
    """Checks if a column exists in a given MySQL table using DESCRIBE"""
    try:
        cursor.execute(f"DESCRIBE `{table_name}` `{column_name}`")
        result = cursor.fetchone()
        return result is not None
    except mysql.connector.Error:
        return False


def main():
    # Read the exporter config YAML file
    with open(configfname) as f:
        config = yaml.load(f, Loader=SafeLoader)
        polling_interval_minutes = config["polling_interval_minutes"]
        mysql_host = config["mysql_host"]
        mysql_port = config["mysql_port"]
        mysql_user = config["mysql_user"]
        mysql_password = config["mysql_password"]
        mysql_database = config["mysql_database"]
        mysql_retention_days = config["mysql_retention_days"]

    # Create a list of the labels for each metrics to collect
    config_labels = {}
    for collector in config["collectors"]:
        for metric in collector["metrics"]:
            config_labels[metric["metric_name"]] = metric["labels"]


    while True:

        for collector in config["collectors"]:
            try:
                result = sp.run([sys.executable, collector["collector_name"] + ".py"], capture_output=True, text=True, check=True)
                datalist = json.loads(result.stdout, object_hook=datetime_decoder)

                with mysql.connector.connect(host=mysql_host, user=mysql_user, password=mysql_password, database=mysql_database, port=mysql_port) as conn:
                    cursor = conn.cursor()

                    # Clear the metric (drop the table) if the metric is clear-marked
                    for metric in collector["metrics"]:
                        if "metric_clear" in metric:
                            if metric["metric_clear"] == "yes":
                                drop_query = f'DROP TABLE IF EXISTS `{metric["metric_name"]}`'
                                cursor.execute(drop_query)

                    # Loop through all items in the collector output and insert into database
                    table_list = []
                    for dataitem in datalist:
                        label_list = list(dataitem["labels"].keys())
                        if label_list == config_labels[dataitem["metric_name"]]:     # If metric labels matches those in config file
                            insert_mysql_data(cursor, dataitem["metric_name"], dataitem["labels"], dataitem["value"])
                        else:
                            logevent("Label problem for metric " + dataitem["metric_name"])

                        if (dataitem["metric_name"] not in table_list) and ("time" in dataitem["labels"]):
                            table_list.append(dataitem["metric_name"])
                    
                    # Delete data from concerned metrics / tables that is older than mysql_retention_days
                    data_retention(cursor, table_list, "time", mysql_retention_days)

                    conn.commit()
                            
            except Exception as e:
                logevent(str(e))


        seconds_remaining = seconds_to_next_mark(polling_interval_minutes)
        time.sleep(seconds_remaining)

if __name__ == "__main__":
    main()
