import requests
import json
import sys
import os
import datetime
import subprocess
import traceback

"""
This script is a "collector" script that reads metrics from the Advantech routers
and outputs them to standard output in JSON format.
This "collector" script can then be invoked by the "expeca-exporter" script, which then makes the metrics
available for Prometheus metrics "scraping".
"""

eventlogfname = "event.log"             # Output file that will have event message if the script used the "logevent" function
eventlogsize = 3000                     # Number of lines allowed in the event log. Oldest lines are cut.
accessfname = "api_access.json"         # File with API access info in JSON format
shellscriptpath = "./get_conf_adv.sh"   # Script that collects Advantech router config info

os.chdir(sys.path[0])            # Set current directory to script directory

adv_list = [
    {"name": "advantech-01", "ipaddr": "10.10.5.1"},
    {"name": "advantech-02", "ipaddr": "10.10.5.2"},
    {"name": "advantech-03", "ipaddr": "10.10.5.3"},
    {"name": "advantech-04", "ipaddr": "10.10.5.4"},
    {"name": "advantech-05", "ipaddr": "10.10.5.5"},
    {"name": "advantech-06", "ipaddr": "10.10.5.6"},
    {"name": "advantech-07", "ipaddr": "10.10.5.7"},
    {"name": "advantech-08", "ipaddr": "10.10.5.8"}
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


def remove_lines_before_first_brace(input_string):
    """Removes all lines of a multi-line string before the first '{' brace"""
    # Split the input string into individual lines
    lines = input_string.splitlines()

    # Find the index of the first line that begins with '{'
    for i, line in enumerate(lines):
        if line.strip().startswith('{'):
            # Return the lines from the first occurrence of '{' to the end
            return '\n'.join(lines[i:])
    
    # If no line starts with '{', return an empty string
    return ''


def read_adv_config(adv):
    """Reads an Advantech router configuration"""
    advconfig_list = []

    advname = adv["name"]
    ipaddr = adv["ipaddr"]

    try:
        # First part, run the router config shell script to get info
        # Run the shell script and capture the output
        result = subprocess.run(
            ['bash', shellscriptpath, ipaddr],      # Pass the shell script and the argument
            capture_output=True,                    # Capture both stdout and stderr
            text=True,                              # Treat the output as text (string)
            check=True                              # Raise an exception if the command fails
        )

        jsonresponse = remove_lines_before_first_brace(result.stdout)
        response = json.loads(jsonresponse)

        for label1, value1 in response.items():
            for label2, value2 in value1.items():
                advconfig_dict = {
                    "metric_name": "expeca_adv_config",
                    "labels": {
                        "advname": advname,
                        "label1" : label1,
                        "label2" : label2
                    },
                    "value": value2
                }

                advconfig_list.append(advconfig_dict)

    except Exception as e:
        logevent(advname + ": gen: " + str(e))


    try:
        # Second part, get info via GET
        # Run GET corresponding to: curl "http://x.x.x.x:50500/?query=info"

        url = "http://" + ipaddr + ":50500/"
        params = {
            'query': 'info'
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors

        response_dict = response.json()
        
        for label2, value2 in response_dict.items():
            advconfig_dict = {
                "metric_name": "expeca_adv_config",
                "labels": {
                    "advname": advname,
                    "label1" : "1 - Active Connection",
                    "label2" : label2
                },
                "value": value2
            }

            advconfig_list.append(advconfig_dict)       

    except Exception as e:
        logevent(advname + ": Act Conn: " + str(e))
        

    try:
        # Third part, get band info via GET
        # Run GET corresponding to: curl "http://x.x.x.x:50500/?query=bands&net=yyyyy"

        for net in ["gw_band", "lte_band", "nsa_nr5g_band", "nr5g_band"]:
            url = "http://" + ipaddr + ":50500/"
            params = {
                "query": "bands",
                "net"  : net
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors

            response_text = response.text
            lines = response_text.splitlines()

            for line in lines:
                if net in line:
                    last_comma_index = line.rfind(',')
    
                    # Extract the substring after the last comma
                    if last_comma_index != -1:
                        bands = line[last_comma_index + 1:].strip()

                        advconfig_dict = {
                            "metric_name": "expeca_adv_config",
                            "labels": {
                                "advname": advname,
                                "label1" : "2 - Configured Bands",
                                "label2" : net
                            },
                            "value": bands
                        }

                        advconfig_list.append(advconfig_dict)                   

    except Exception as e:
        logevent(advname + ": Conf Bands: " + str(e))


    return advconfig_list


def main():
    
    outp_list = []
    
    for adv in adv_list:
        advconfig_list = read_adv_config(adv)
        outp_list.extend(advconfig_list)
    
    # Output the resulting metrics to standard output, in JSON format
    print(json.dumps(outp_list, indent = 4))

    return


if __name__ == "__main__":
    main()
