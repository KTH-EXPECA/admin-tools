import requests
import json
import sys
import os
from datetime import datetime
import traceback
import time

"""
This script is a "collector" script that reads equipment status from the ExPECA testbed
and outputs them to standard output in JSON format.
This "collector" script can then be invoked by the "expeca-exporter" script, which then makes the metrics
available for Prometheus metrics "scraping".
"""

eventlogfname = "event.log"         # Output file that will have event message if the script used the "logevent" function
eventlogsize = 3000                 # Number of lines allowed in the event log. Oldest lines are cut.
accessfname = "equipm_access.json"  # File with equipment check url info in JSON format

os.chdir(sys.path[0])            # Set current directory to script directory



sdr_list = [
    {
        "name"    : "sdr-01",
        "ni-ip"   : "10.30.10.2",
        "mango-ip": "10.30.1.1"
    },
    {
        "name"    : "sdr-02",
        "ni-ip"   : "10.30.10.4",
        "mango-ip": "10.30.1.3"
    },
    {
        "name"    : "sdr-03",
        "ni-ip"   : "10.30.10.6",
        "mango-ip": "10.30.1.5"
    },
    {
        "name"    : "sdr-04",
        "ni-ip"   : "10.30.10.8",
        "mango-ip": "10.30.1.7"
    },
    {
        "name"    : "sdr-05",
        "ni-ip"   : "10.30.10.10",
        "mango-ip": "10.30.1.9"
    },
    {
        "name"    : "sdr-06",
        "ni-ip"   : "10.30.10.12",
        "mango-ip": "10.30.1.11"
    },
    {
        "name"    : "sdr-07",
        "ni-ip"   : "10.30.10.14",
        "mango-ip": "10.30.1.13"
    },
    {
        "name"    : "sdr-08",
        "ni-ip"   : "10.30.10.16",
        "mango-ip": "10.30.1.15"
    },
    {
        "name"    : "sdr-09",
        "ni-ip"   : "10.30.10.18",
        "mango-ip": "10.30.1.17"
    },
    {
        "name"    : "sdr-10",
        "ni-ip"   : "10.30.10.20",
        "mango-ip": "10.30.1.19"
    }
]


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


def equipm_readaccess(accessfname):
    """
    Reads Equipment check URL data from a JSON file.

    Reads Equipment check URL data from a JSON file.
    Input: URL info file name
    Return: Dictionary with URL information, or exception
    """
    try:
        with open(accessfname, 'r') as f:
            return json.load(f)
    except Exception as e:
        return e  
    

def read_sdr_data(accessinfo):
    """
    Reads the SDR data from the "expeca-controller" container

    Reads the SDR data from the "expeca-controller" container.
    Input: URL info file name
    Return: List of dictionaries with SDR info, could be empty if some error happened.
    """

    sdr_data_list = []

    for sdr in sdr_list:

        try:
            sdrnum = sdr["name"].split("-")[1]
            url = accessinfo["url"]
            params = {
                'name': sdr["name"]
            }

            response = requests.get(url, params=params)       
            response.raise_for_status()
            responsedata = response.json()

            if responsedata != {}:
                if "linkstate" in responsedata["sdr_" + sdrnum + "_mango"]:
                    linkstate = responsedata["sdr_" + sdrnum + "_mango"]["linkstate"]
                else:
                    linkstate = "Unknown"

                if "type" in responsedata["sdr_" + sdrnum + "_mango"]:
                    type = responsedata["sdr_" + sdrnum + "_mango"]["type"]
                else:
                    type = "10G-Copper"

                if linkstate == "Up":
                    status = 1
                elif linkstate == "Down":
                    status = 0
                else:
                    status = -1
                    
                sdr_data__dict = {
                    "metric_name": "expeca_sdr_status",
                    "labels": {
                        "sdr": sdr["name"],
                        "mode": "mango",
                        "ip": sdr["mango-ip"],
                        "type": type
                    },
                    "value": status
                }

                sdr_data_list.append(sdr_data__dict)

                if "linkstate" in responsedata["sdr_" + sdrnum + "_ni"]:
                    linkstate = responsedata["sdr_" + sdrnum + "_ni"]["linkstate"]
                else:
                    linkstate = "Unknown"

                if "type" in responsedata["sdr_" + sdrnum + "_ni"]:
                    type = responsedata["sdr_" + sdrnum + "_ni"]["type"]
                else:
                    type = "10G-Fiber"

                if linkstate == "Up":
                    status = 1
                elif linkstate == "Down":
                    status = 0
                else:
                    status = -1

                sdr_data__dict = {
                    "metric_name": "expeca_sdr_status",
                    "labels": {
                        "sdr": sdr["name"],
                        "mode": "ni",
                        "ip": sdr["ni-ip"],
                        "type": type
                    },
                    "value": status
                }

                sdr_data_list.append(sdr_data__dict)

        except Exception as e:
            logevent(sdr["name"] + ": " + str(e))

    return sdr_data_list


def main():

    outp_list = []
    accessinfo = equipm_readaccess(accessfname)
    if isinstance(accessinfo, Exception):
        logevent(str(accessinfo))
        return

    sdr_data_list = read_sdr_data(accessinfo)
    outp_list.extend(sdr_data_list)

    # Output the resulting metrics to standard output, in JSON format
    print(json.dumps(outp_list, indent = 4))

    return


if __name__ == "__main__":
    main()
