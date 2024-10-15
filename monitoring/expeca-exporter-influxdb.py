import time
import json
import sys
import os
import subprocess as sp
import yaml
from yaml.loader import SafeLoader
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import traceback

"""
This script is an exporter for InfluxDB metrics.
It takes metrics from "collector" scripts in JSON format, and pushes them to InfluxDB.
A config file in YAML format defines the collector scripts (separate Python scripts) and their corresponding metrics,
so that new collectors and/or metrics can be added easily.
Usage: python3 expeca-exporter-influxdb.py &
"""

configfname = "expeca-exporter-influxdb.yml"          # YAML file with collector config
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
    keylist = []
    valuelist = []
    for key, value in in_dict.items():
        keylist.append(key)
        valuelist.append(value)
    return keylist, valuelist

def seconds_to_next_mark(polling_interval_minutes):
    """Calculates the number of seconds remaining to the next x-minute mark on the clock"""
    now = datetime.now()
    # Calculate the number of seconds since the last mark
    seconds_since_last_mark = (now.minute % polling_interval_minutes) * 60 + now.second
    # Calculate the number of seconds to the next x-minute mark
    seconds_to_next_mark = polling_interval_minutes * 60 - seconds_since_last_mark
    return seconds_to_next_mark


def main():
    # Read the exporter config YAML file
    with open(configfname) as f:
        config = yaml.load(f, Loader=SafeLoader)
        polling_interval_minutes = config["polling_interval_minutes"]
        influxdb_url = config["influxdb_url"]
        influxdb_token = config["influxdb_token"]
        influxdb_org = config["influxdb_org"]
        influxdb_bucket = config["influxdb_bucket"]

    # InfluxDB metrics to collect
    config_labels = {}
    for collector in config["collectors"]:
        for metric in collector["metrics"]:
            config_labels[metric["metric_name"]] = metric["labels"]

    while True:

        for collector in config["collectors"]:
            try:
                result = sp.run([sys.executable, collector["collector_name"] + ".py"], capture_output=True, text=True, check=True)
                datalist = json.loads(result.stdout)

                with InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org) as client:
                    write_api = client.write_api(write_options=SYNCHRONOUS)

                    for dataitem in datalist:
                        # Prepare data point for InfluxDB
                        label_list, value_list = dict_to_lists(dataitem["labels"])
                        if label_list == config_labels[dataitem["metric_name"]]:
                            point = Point(dataitem["metric_name"])                    # .tag("source", collector["collector_name"])
                            if "time" in dataitem["labels"]:
                                timestamp = dataitem["labels"].pop("time")
                                timestamp_dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
                                point = point.time(timestamp_dt, WritePrecision.S)
                            for label_key, label_value in dataitem["labels"].items():
                                point = point.tag(label_key, label_value)
                            point = point.field("value", dataitem["value"])

                            write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point, precision="m")
                        else:
                            logevent("Label problem for metric " + dataitem["metric_name"])
                            # logevent("Config labels:", config_labels[dataitem["metric_name"]])
                            # logevent("Collector labels:", label_list)
                            
            except Exception as e:
                logevent(str(e))


        seconds_remaining = seconds_to_next_mark(polling_interval_minutes)
        time.sleep(seconds_remaining)

if __name__ == "__main__":
    main()
