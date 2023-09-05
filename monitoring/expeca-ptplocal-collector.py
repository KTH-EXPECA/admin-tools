#!/usr/bin/env python

# This script collects PTP metrics from the worker node. It does so by collecting
# data from the syslog. The metrics are output in JSON format that can be read by the expeca-exporter.py script
# which makes the metrics available for Prometheus.
# Usage:
# python3 ./expeca-ptplocal-collector.py

import sys
import os
import json
from datetime import datetime
from statistics import stdev
import subprocess

eventlogfname = "event.log"      # Output file that will have event message if the script used the "logevent" function
eventlogsize = 3000              # Number of lines allowed in the event log. Oldest lines are cut.


os.chdir(sys.path[0])      # Set current directory to script directory


# Writes time stamp plus text into event log file
def logevent(logtext):

    try:
        with open(eventlogfname, "r") as f:
            lines = f.read().splitlines()
        newlines = lines[-eventlogsize:]
    except:
        newlines = []

    with open(eventlogfname, "w") as f:
        for line in newlines:
            f.write(line + "\n")
        now = datetime.now()
        date_time = now.strftime("%Y/%m/%d %H:%M:%S")
        f.write(date_time + " " + logtext + "\n")

    return



def main():

    now = datetime.now()
    outp_list = []


    command = "hostname"
    cmdoutput = subprocess.check_output(command, shell=True)
    linelist = cmdoutput.decode().splitlines()
    HOSTNAME = linelist[0]

    command = "cat /var/log/syslog | grep ptp4l | grep 'master offset' | tail -n 720"
    cmdoutput = subprocess.check_output(command, shell=True)
    linelist = cmdoutput.decode().splitlines()

    offset_list = []
    for line in linelist:
        wordlist = line.split()

        if len(wordlist) == 15:
            timestampstr = str(now.year) + " " + wordlist[0] + " " + wordlist[1] + " " + wordlist[2]
            timestamp = datetime.strptime(timestampstr, "%Y %b %d %H:%M:%S")
            timedelta = now - timestamp

            if timedelta.total_seconds() < 365:                 # Only use logs from within last 6 minutes
                offset = int(wordlist[8])
                offset_list.append(offset)

    if len(offset_list) > 0:
        stdoffset = stdev(offset_list)
        maxoffset = max(offset_list)
        minoffset = min(offset_list)
    
        outp = {
            "metric_name": "expeca_ptp_hwstdoffset",
            "labels": {
                "host": HOSTNAME
            },
            "value": stdoffset
        }

        outp_list.append(outp)

        outp = {
            "metric_name": "expeca_ptp_hwmaxoffset",
            "labels": {
                "host": HOSTNAME
            },
            "value": maxoffset
        }

        outp_list.append(outp)

        outp = {
            "metric_name": "expeca_ptp_hwminoffset",
            "labels": {
                "host": HOSTNAME
            },
            "value": minoffset
        }

        outp_list.append(outp)



    command = "cat /var/log/syslog | grep phc2sys | grep 'phc offset' | tail -n 720"
    cmdoutput = subprocess.check_output(command, shell=True)
    linelist = cmdoutput.decode().splitlines()

    offset_list = []
    for line in linelist:
        wordlist = line.split()

        if len(wordlist) == 15:
            timestampstr = str(now.year) + " " + wordlist[0] + " " + wordlist[1] + " " + wordlist[2]
            timestamp = datetime.strptime(timestampstr, "%Y %b %d %H:%M:%S")
            timedelta = now - timestamp

            if timedelta.total_seconds() < 365:                 # Only use logs from within last 6 minutes
                offset = int(wordlist[9])
                offset_list.append(offset)

    if len(offset_list) > 0:
        stdoffset = stdev(offset_list)
        maxoffset = max(offset_list)
        minoffset = min(offset_list)
    
        outp = {
            "metric_name": "expeca_ptp_swstdoffset",
            "labels": {
                "host": HOSTNAME
            },
            "value": stdoffset
        }

        outp_list.append(outp)

        outp = {
            "metric_name": "expeca_ptp_swmaxoffset",
            "labels": {
                "host": HOSTNAME
            },
            "value": maxoffset
        }

        outp_list.append(outp)

        outp = {
            "metric_name": "expeca_ptp_swminoffset",
            "labels": {
                "host": HOSTNAME
            },
            "value": minoffset
        }

        outp_list.append(outp)



    print(json.dumps(outp_list, indent = 4))
    if len(outp_list) == 0:
        logevent("Empty PTP list")

    return



if __name__ == "__main__":
    # logevent("PTP start")
    main()
    # logevent("PTP stop")


