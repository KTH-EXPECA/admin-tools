import time
from prometheus_client import start_http_server, Gauge, Counter
import json
import sys
import os
import subprocess as sp
import yaml
from yaml.loader import SafeLoader
from datetime import datetime
import traceback

"""
This script is an exporter for Prometheus metrics.
It takes metrics from "collector" scripts in JSON format, and exposes them on a specific port so that Prometheus
can "scrape" the metrics into its database.
A config file in YAML format defines the collector scripts (separate Python scripts) and their corresponding metrics,
so that new collectors and/or metrics can be added easily.
Usage: python3 expeca-exporter.py &
"""

configfname = "expeca-exporter.yml"          # YAML file with collector config
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
    """Calculates the number of seconds to next 5-minute mark"""
    now = datetime.now()
    # Calculate the number of seconds since the last mark
    seconds_since_last_mark = (now.minute % polling_interval_minutes) * 60 + now.second
    # Calculate the number of seconds to the next 5-minute mark
    seconds_to_next_mark = 300 - seconds_since_last_mark
    return seconds_to_next_mark


def main():

    # Read the exporter config YAML file
    with open(configfname) as f:
        config = yaml.load(f, Loader=SafeLoader)
        polling_interval_minutes = config["polling_interval_minutes"]
        exporter_port = config["exporter_port"]

    # Expose the given port for Prometheus "scraping"
    start_http_server(exporter_port)

    # Prometheus metrics to collect
    metric_dict = {}
    config_labels = {}
    for collector in config["collectors"]:
        for metric in collector["metrics"]:
            if metric["metric_type"] == "gauge":
                metric_item = Gauge(metric["metric_name"], metric["metric_descr"], metric["labels"])
            elif metric["metric_type"] == "counter":
                metric_item = Counter(metric["metric_name"], metric["metric_descr"], metric["labels"])
            else:
                # faulty metric type
                metric_item = metric["metric_name"] + " has wrong type: " + metric["metric_type"] + " (only gauge or counter is allowed)"
                logevent(metric_item)

            metric_dict[metric["metric_name"]] = metric_item
            config_labels[metric["metric_name"]] = metric["labels"]

    while True:

        for collector in config["collectors"]:
            try:
                result = sp.run([sys.executable, collector["collector_name"] + ".py"], capture_output=True, text=True, check=True)
                datalist = json.loads(result.stdout)

                for metric in collector["metrics"]:
                    metric_dict[metric["metric_name"]].clear()

                for dataitem in datalist:
                    # Update Prometheus metrics
                    metric_item = metric_dict[dataitem["metric_name"]]
                    if type(metric_item) is not str:                                          # if valid metric type
                        label_list, value_list = dict_to_lists(dataitem["labels"])
                        if label_list == config_labels[dataitem["metric_name"]]:
                            metric_item.labels(*value_list).set(dataitem["value"])
                        else:
                            logevent("Label problem for metric " + dataitem["metric_name"])
                            # logevent("Config labels:", config_labels[dataitem["metric_name"]])
                            # logevent("Collector labels:", label_list)

            except Exception as e:
                logevent(str(e))    
                            
        seconds_remaining = seconds_to_next_mark(polling_interval_minutes)

        # time.sleep(polling_interval_seconds)
        time.sleep(seconds_remaining)



if __name__ == "__main__":
    main()

