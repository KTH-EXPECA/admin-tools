import requests
import json
import sys
import os
import datetime

"""
This script is a "collector" script that reads metrics from the Ericsson Private 5G platform
and outputs them to standard output in JSON format.
This "collector" script can then be invoked byt the "expeca-exporter" script, which then makes the metrics
available for Prometheus metrics "scraping".
"""

os.chdir(sys.path[0])            # Set current directory to script directory

accessfname = "api_access.json"           # File with API access info in JSON format


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


def ep5g_get(accessinfo, tailurl):
    """
    Reads EP5G data via API GET.

    Reads EP5G data via API GET.
    Input 1: Access info as a dictionary
    Input 2: Tail part of URL used in GET request, starting with "forward slash". Example: "/kpi/latency"
    Return: class 'requests.models.Response' or exception
    """
    url = accessinfo["baseurl"] + "/organization/" + accessinfo["orgid"] + "/site/" + accessinfo["siteid"] + tailurl
    headers = {"x-api-key": accessinfo["key"]}
    try:
        return requests.get(url, headers=headers)
    except Exception as e:
        return e
    

def get_average(datalist):
    """Returns the avarage of "dataPoint" values in a list"""
    sum = 0
    numitems = 0
    for dataitem in datalist:
        sum += float(dataitem["dataPoint"])
        numitems += 1
    average = sum / numitems

    return average


def read_ep5g_latency(accessinfo):
    """
    Reads the "latency" metric from EP5G

    Reads the "latency" metric from EP5G, which is only available if the watchdog application is running.
    Returned is the average latency over the last 5 minutes.
    """
    latency_list = []
    response_ok = False
    tailurl = "/kpi/latency"
    apiresponse = ep5g_get(accessinfo, tailurl)
    
    if type(apiresponse) is requests.models.Response:
        if apiresponse.ok:
            responsedata = apiresponse.json()   # responsedata = dictionary or list of dictionaries
            response_ok = True
        else:
            print("#", "Response status code:")
            print("#", apiresponse.status_code)
    else:
        print("#", "Exception:")
        print("#", type(apiresponse))
        print("#", apiresponse)

    if response_ok and responsedata != {}:
        for user, user_list in responsedata["watchdogs"].items():
            last_item = user_list[-1]
            # print(user_list[-5:])
            # print(str(get_average(user_list[-5:])))

            dt = datetime.datetime.fromtimestamp(float(last_item["timeStamp"]))
            dtnow = datetime.datetime.now()
            delta = dtnow - dt

            if (last_item["dataPoint"] != "") and (delta.total_seconds() < 600):
                latency_dict = {
                    "metric_name": "expeca_ep5g_latency",
                    "labels": {
                        "user": user
                    },
                    # "value": last_item["dataPoint"]
                    "value": get_average(user_list[-5:])
                }

                latency_list.append(latency_dict)

    return latency_list


def read_ep5g_throughput(accessinfo):
    """
    Reads the "throughput" metric from EP5G.

    Reads the "throughput" metric from EP5G.
    Returned is the average throughput over the last 5 minutes for the whole EP5G system.
    """
    throughput_list = []
    response_ok = False
    tailurl = "/kpi/throughput"
    apiresponse = ep5g_get(accessinfo, tailurl)
    
    if type(apiresponse) is requests.models.Response:
        if apiresponse.ok:
            responsedata = apiresponse.json()   # responsedata = dictionary or list of dictionaries
            response_ok = True
        else:
            print("#", "Response status code:")
            print("#", apiresponse.status_code)
    else:
        print("#", "Exception:")
        print("#", type(apiresponse))
        print("#", apiresponse)

    if response_ok and responsedata != {}:
        throughput_dict = {
            "metric_name": "expeca_ep5g_throughput",
            "labels": {
                "direction": "downlink"
            },
            "value": responsedata["avgDownlink"]
        }

        throughput_list.append(throughput_dict)

        throughput_dict = {
            "metric_name": "expeca_ep5g_throughput",
            "labels": {
                "direction": "uplink"
            },
            "value": responsedata["avgUplink"]
        }

        throughput_list.append(throughput_dict)

    return throughput_list


def read_ep5g_imsi_datausage(accessinfo):
    """
    Reads the "datausage" metric from EP5G.
    
    Reads the "datausage" metric from EP5G.
    Returned is the average throughput over the last 5 minutes, per IMSI
    """
    imsi_datausage_list = []
    response_ok = False
    tailurl = "/nc/imsi"
    apiresponse = ep5g_get(accessinfo, tailurl)
    
    if type(apiresponse) is requests.models.Response:
        if apiresponse.ok:
            responsedata = apiresponse.json()   # responsedata = dictionary or list of dictionaries
            response_ok = True
        else:
            print("#", "Response status code:")
            print("#", apiresponse.status_code)
    else:
        print("#", "Exception:")
        print("#", type(apiresponse))
        print("#", apiresponse)

    if response_ok and responsedata != {}:
        for imsi_item in responsedata:
            imsi = imsi_item["imsi"]
            response_ok = False
            tailurl = "/nc/imsi/" + imsi + "/datausage?timespan=1"
            apiresponse = ep5g_get(accessinfo, tailurl)
    
            if type(apiresponse) is requests.models.Response:
                if apiresponse.ok:
                    responsedata = apiresponse.json()   # responsedata = dictionary or list of dictionaries
                    response_ok = True
                else:
                    print("#", "Response status code:")
                    print("#", apiresponse.status_code)
            else:
                print("#", "Exception:")
                print("#", type(apiresponse))
                print("#", apiresponse)      

            if response_ok and responsedata != {}:
                # print(responsedata)
                # exit()
                if responsedata:
                    data_list = responsedata["downlink"]
                    last_item = data_list[-1]

                    dt = datetime.datetime.fromtimestamp(float(last_item["timeStamp"]))
                    dtnow = datetime.datetime.now()
                    delta = dtnow - dt

                    if (last_item["dataPoint"] != "") and (delta.total_seconds() < 600):
                        imsi_datausage_dict = {
                            "metric_name": "expeca_ep5g_imsi_datausage",
                            "labels": {
                                "imsi": imsi,
                                "direction": "downlink"
                            },
                            # "value": last_item["dataPoint"]
                            "value": get_average(data_list[-5:])
                        }

                        imsi_datausage_list.append(imsi_datausage_dict)

                    data_list = responsedata["uplink"]
                    last_item = data_list[-1]
                    if last_item["dataPoint"] != "":
                        imsi_datausage_dict = {
                            "metric_name": "expeca_ep5g_imsi_datausage",
                            "labels": {
                                "imsi": imsi,
                                "direction": "uplink"
                            },
                            # "value": last_item["dataPoint"]
                            "value": get_average(data_list[-5:])
                        }

                        imsi_datausage_list.append(imsi_datausage_dict)

    return imsi_datausage_list


def main():
    
    outp_list = []
    accessinfo = ep5g_readaccess(accessfname)

    latency_list = read_ep5g_latency(accessinfo)
    outp_list.extend(latency_list)

    throughput_list = read_ep5g_throughput(accessinfo)
    outp_list.extend(throughput_list)
                    
    imsi_datausage_list = read_ep5g_imsi_datausage(accessinfo)
    outp_list.extend(imsi_datausage_list)

    # Output the resulting metrics to standard output, in JSON format
    print(json.dumps(outp_list, indent = 4))

    return


if __name__ == "__main__":
    main()
