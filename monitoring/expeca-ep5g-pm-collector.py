import requests
import json
import sys
import os
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
import tarfile
import io
import gzip
import traceback

"""
This script is a "collector" script that reads metrics from the Ericsson Private 5G platform
and outputs them to standard output in JSON format.
This "collector" script can then be invoked byt the "expeca-exporter" script, which then makes the metrics
available for Prometheus metrics "scraping" or sends it to an InfluxDB database.
"""

accessfname = "api_access.json"           # File with API access info in JSON format
namespace = {'ns': 'http://www.3gpp.org/ftp/specs/archive/32_series/32.435#measCollec'}

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


def extract_xml_from_tarball(tarball_binary):
    """Extracts XML files from a tarball, and returns a list of XML contents, one per file"""
    xml_list = []

    # Create a file-like object from the binary input
    tarball_file = io.BytesIO(tarball_binary)

    # Open the tarball
    with tarfile.open(fileobj=tarball_file) as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith('.xml.gz'):
                # Extract the gzip file content
                gz_file = tar.extractfile(member)
                if gz_file:
                    with gzip.open(gz_file) as f:
                        xml_content = f.read()
                        # Add the XML content to the list
                        xml_list.append(xml_content.decode('utf-8'))

    return xml_list


def extract_measurements(meas_info):
    """Function to extract measurements from measInfo (XML content)"""
    meas_types = {mt.attrib['p']: mt.text for mt in meas_info.findall('ns:measType', namespace)}
    values = []
    for meas_value in meas_info.findall('ns:measValue', namespace):
        obj_ldn = meas_value.attrib['measObjLdn']
        measurements = {meas_types[r.attrib['p']]: r.text for r in meas_value.findall('ns:r', namespace)}
        measurements['measObjLdn'] = obj_ldn
        values.append(measurements)
    return values


def ep5g_readaccess(accessfname):
    """
    Reads EP5G access information data from a JSON file.

    Reads EP5G access information data from a JSON file.
    Input: Access info file name
    Return: Dictionary with API access information, or exception string
    """
    try:
        with open(accessfname, 'r') as f:
            return json.load(f)
    except Exception as e:
        return e   


def ep5g_get(accessinfo, tailurl, params=None):
    """
    Reads EP5G data via API GET.

    Reads EP5G data via API GET.
    Input 1: Access info as a dictionary
    Input 2: Tail part of URL used in GET request, starting with "forward slash". Example: "/kpi/latency"
    Input 3: Optional query parameters used in GET request, in format of a dictionary
    Return: class 'requests.models.Response' or exception
    """
    url = accessinfo["baseurl"] + "/organization/" + accessinfo["orgid"] + "/site/" + accessinfo["siteid"] + tailurl
    headers = {"x-api-key": accessinfo["key"]}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response
    except Exception as e:
        return e
    

def read_ep5g_pm(accessinfo):
    """Reads the "pm" metric from EP5G"""
    pm_list = []

    try:
        tailurl = "/pm"

        now = datetime.now(timezone.utc) - timedelta(minutes=10)
        minute = (now.minute // 15) * 15
        current_quarter_hour = now.replace(minute=minute, second=0, microsecond=0)
        previous_quarter_hour = current_quarter_hour - timedelta(minutes=15)

        # Format the previous quarter hour as an RFC3339 timestamp
        start = previous_quarter_hour.replace(tzinfo=None).isoformat() + "Z"
        end = current_quarter_hour.replace(tzinfo=None).isoformat() + "Z"

        query_params = {
            "start": start,
            "end"  : end, 
        }
        
        apiresponse = ep5g_get(accessinfo, tailurl, query_params)
        if isinstance(apiresponse, Exception):
            logevent(str(apiresponse))
            return pm_list
        
        xmlstrs = extract_xml_from_tarball(apiresponse.content)
        meas_list = []

        # numfiles = len(xmlstrs)
        # logevent(numfiles)

        for xmlstr in xmlstrs:
            root = ET.fromstring(xmlstr)

            # Extract data from measData
            for meas_info in root.findall('.//ns:measInfo', namespace):
                meas_info_id = meas_info.attrib['measInfoId']
                job_id = meas_info.find('ns:job', namespace).attrib['jobId']
                period = meas_info.find('ns:granPeriod', namespace).attrib['duration']
                end_time = meas_info.find('ns:granPeriod', namespace).attrib['endTime']

                dt = datetime.fromisoformat(end_time)
                end_time = dt.strftime('%Y-%m-%dT%H:%M:%SZ')

                measurements = extract_measurements(meas_info)
                for measurement in measurements:
                    measurement.update({
                        'measInfoId': meas_info_id,
                        # 'jobId': job_id,
                        # 'granPeriod': period,
                        'endTime': end_time
                    })
                    meas_list.append(measurement)


        if meas_list != []:
            for measurement in meas_list:
                for key, values in measurement.items():
                    if (key != "measInfoId") and (key != "measObjLdn") and (key != "endTime"):
                        valuelist = values.split(',')
                        for index, value in enumerate(valuelist):
                            if value.strip() != "":
                                pm_dict = {
                                    "metric_name": "expeca_ep5g_pm",
                                    "labels": {
                                        "measInfoId": measurement["measInfoId"],
                                        "measObjLdn": measurement["measObjLdn"],
                                        "time"      : measurement["endTime"],
                                        "measName"  : key,
                                        "index"     : index,
                                    },
                                    "value": int(float(value.strip())) 
                                }

                                pm_list.append(pm_dict)

    except Exception as e:
        logevent(str(e))
        
    return pm_list



def main():
    
    outp_list = []
    accessinfo = ep5g_readaccess(accessfname)

    if isinstance(accessinfo, Exception):
        logevent(str(accessinfo))
        return
        
    pm_list = read_ep5g_pm(accessinfo)
    outp_list.extend(pm_list)

    # Output the resulting metrics to standard output, in JSON format
    print(json.dumps(outp_list, indent = 4))

    return


if __name__ == "__main__":
    main()
