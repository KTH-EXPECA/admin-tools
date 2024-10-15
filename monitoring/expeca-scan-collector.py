#!/usr/bin/env python
#
import sys
import os
import json
import paramiko
from datetime import datetime
import traceback


eventlogfname = "event.log"      # Output file that will have event message if the script used the "logevent" function
eventlogsize = 3000              # Number of lines allowed in the event log. Oldest lines are cut.

os.chdir(sys.path[0])      # Set current directory to script directory

HOST = "10.10.1.1"
USER = 'expeca'
SSHKEY = '/home/expeca/.ssh/id_rsa'


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


def main():

    outp_list = []

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file(SSHKEY)
        client.connect(hostname=HOST, disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}, username=USER, pkey=pkey)

        command = "JSON_PATH=all.json python scan.py"
        stdin, stdout, stderr = client.exec_command(command)
        bytelinelist = stdout.read().splitlines()  

        linelist = []
        for byteline in bytelinelist:
            linelist.append(byteline.decode())

        for line in linelist:
            wordlist = line.split()
            if len(wordlist) == 4:
                if wordlist[0] != "HOST":
                    host = wordlist[0]
                    ipaddress = wordlist[1]
                    port = wordlist[2]
                    statusstr = wordlist[3]

                    if statusstr == "Up":
                        status = 1
                    else:
                        status = 0

                    outp = {
                        "metric_name": "expeca_dev_status",
                        "labels": {
                            "host": host,
                            "ipaddress": ipaddress,
                            "port": port
                        },
                        "value": status
                    }

                    outp_list.append(outp)

    except Exception as e:
        logevent(str(e))
                                                         
    print(json.dumps(outp_list, indent = 4))

    return



if __name__ == "__main__":
    main()

