import requests
import json
import sys
import os
from datetime import datetime, timedelta, timezone
import zlib
import xml.etree.ElementTree as ET
import tarfile
import io
import gzip

"""
This script is a "collector" script that reads metrics from the Ericsson Private 5G platform
and outputs them to standard output in JSON format.
This "collector" script can then be invoked byt the "expeca-exporter" script, which then makes the metrics
available for Prometheus metrics "scraping".
"""

os.chdir(sys.path[0])            # Set current directory to script directory

accessfname = "api_access.json"           # File with API access info in JSON format
namespace = {'ns': 'http://www.3gpp.org/ftp/specs/archive/32_series/32.435#measCollec'}

eventlogfname = "event.log"      # Output file that will have event message if the script used the "logevent" function
eventlogsize = 3000              # Number of lines allowed in the event log. Oldest lines are cut.


def extract_xml_from_tarball(tarball_binary):
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


# Function to extract measurements from measInfo
def extract_measurements(meas_info):
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
    Return: Dictionary with API access information, or exception
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
        return requests.get(url, headers=headers, params=params)
    except Exception as e:
        return e
    

def read_ep5g_pm(accessinfo):
    """
    Reads the "pm" metric from EP5G.
    """
    pm_list = []
    response_ok = False
    # tailurl = "/pm?start=2024-06-04T09:00:00Z&end=2024-06-04T09:15:00Z"
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

    # logevent("expeca-ep5g-pm-collector: now: " + str(datetime.now(timezone.utc)) + "   start: " + str(start) + "   end: " + str(end))
    
    apiresponse = ep5g_get(accessinfo, tailurl, query_params)
    
    if type(apiresponse) is requests.models.Response:
        if apiresponse.ok:
            xmlstrs = extract_xml_from_tarball(apiresponse.content)
            meas_list = []

            for xmlstr in xmlstrs:
                root = ET.fromstring(xmlstr)

                # Extract data from measData
                for meas_info in root.findall('.//ns:measInfo', namespace):
                    meas_info_id = meas_info.attrib['measInfoId']
                    job_id = meas_info.find('ns:job', namespace).attrib['jobId']
                    period = meas_info.find('ns:granPeriod', namespace).attrib['duration']
                    end_time = meas_info.find('ns:granPeriod', namespace).attrib['endTime']
                    measurements = extract_measurements(meas_info)
                    for measurement in measurements:
                        measurement.update({
                            'measInfoId': meas_info_id,
                            # 'jobId': job_id,
                            # 'granPeriod': period,
                            # 'endTime': end_time
                        })
                        meas_list.append(measurement)

            response_ok = True
        else:
            print("#", "Response status code:")
            print("#", apiresponse.status_code)
            logevent("expeca-ep5g-pm-collector: Response status code: " + str(apiresponse.status_code))
    else:
        print("#", "Exception:")
        print("#", type(apiresponse))
        print("#", apiresponse)
        logevent("expeca-ep5g-pm-collector: Exception: " + str(apiresponse))

    if response_ok and meas_list != []:

        for measurement in meas_list:
            for key, values in measurement.items():
                if (key != "measInfoId") and (key != "measObjLdn"):
                    valuelist = values.split(',')
                    for index, value in enumerate(valuelist):
                        if value.strip() != "":
                            pm_dict = {
                                "metric_name": "expeca_ep5g_pm",
                                "labels": {
                                    "measInfoId": measurement["measInfoId"],
                                    "measObjLdn": measurement["measObjLdn"],
                                    "measName"  : key,
                                    "index"     : index,
                                },
                                # "value": value.split(',')[0].strip()   # Use only first value if values are comma separated list
                                "value": value.strip()   # Use only first value if values are comma separated list
                            }

                            pm_list.append(pm_dict)

    return pm_list



def main():
    
    outp_list = []
    accessinfo = ep5g_readaccess(accessfname)

    pm_list = read_ep5g_pm(accessinfo)
    outp_list.extend(pm_list)

    # Output the resulting metrics to standard output, in JSON format
    print(json.dumps(outp_list, indent = 4))

    return


if __name__ == "__main__":
    main()
