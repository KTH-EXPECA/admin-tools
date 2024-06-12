import time
from prometheus_client import start_http_server, Gauge, Counter
import json
import sys
import os
import subprocess as sp
import yaml
from yaml.loader import SafeLoader
from datetime import datetime

"""
This script is an exporter for Prometheus metrics.
It takes metrics from "collector" scripts in JSON format, and exposes them on a specific port so that Prometheus
can "scrape" the metrics into its database.
A config file in YAML format defines the collector scripts (separate Python scripts) and their corresponding metrics,
so that new collectors and/or metrics can be added easily.
Usage: python3 expeca-exporter.py &
"""

eventlogfname = "event.log"      # Output file that will have event message if the script used the "logevent" function
eventlogsize = 3000              # Number of lines allowed in the event log. Oldest lines are cut.

os.chdir(sys.path[0])            # Set current directory to script directory


def logevent(logtext):
    """
    Writes time stamp plus text into event log file.

    Writes time stamp plus text into event log file. If max number of lines are reached, old lines are cut.
    If an exception occurs, nothing is done (pass).
    """

    try:
        with open(eventlogfname, "r") as f:
            lines = f.read().splitlines()
        newlines = lines[-eventlogsize:]

        with open(eventlogfname, "w") as f:
            for line in newlines:
                f.write(line + "\n")
            now = datetime.now()
            date_time = now.strftime("%Y/%m/%d %H:%M:%S")
            f.write(date_time + " " + logtext + "\n")
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
    now = datetime.now()
    # Calculate the number of seconds since the last mark
    seconds_since_last_mark = (now.minute % polling_interval_minutes) * 60 + now.second
    # Calculate the number of seconds to the next 5-minute mark
    seconds_to_next_mark = 300 - seconds_since_last_mark
    return seconds_to_next_mark


def main():

    # Read the exporter config YAML file
    with open('expeca-exporter.yml') as f:
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

    pm_counter = 0   # Makes sure EP5G PM data is only fetched every 15 minutes

    while True:

        # logevent("Exporter round start")

        pm_counter += 1
        if pm_counter > 2:
            pm_counter = 0

        for collector in config["collectors"]:
            if collector["collector_name"] == "expeca-ep5g-pm-collector":
                if pm_counter != 1:
                    continue

            try:
                result = sp.run([sys.executable, collector["collector_name"] + ".py"], capture_output=True, text=True, check=True)
                datalist = json.loads(result.stdout)
                collector_ok = True
                # print(collector["collector_name"] + " ok")
            except:
                collector_ok = False
                # logevent("expeca_exporter: Collector " + collector["collector_name"] + " failed")
                # print(collector["collector_name"] + " Not ok")

            for metric in collector["metrics"]:
                metric_dict[metric["metric_name"]].clear()


            if collector_ok:

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
                        


        seconds_remaining = seconds_to_next_mark(polling_interval_minutes)
        # print(f"Seconds left to the next 5-minute mark: {seconds_remaining}")

        # time.sleep(polling_interval_seconds)
        time.sleep(seconds_remaining)



if __name__ == "__main__":
    main()

