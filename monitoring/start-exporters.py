#!/usr/bin/env python

# This script restarts monitor services on controller and all worker nodes. It does so by restarting expeca-exporter on controller
# node, if the process is not already running.
# It then connects to each of the worker nodes and restarts node_exporter process, if the process is not already running.
# Usage:
# python3 ./monitor-start

import sys
import os
import paramiko
import subprocess


os.chdir(sys.path[0])      # Set current directory to script directory

# Define hosts to get metrics from
host_list = [
    {
        "hostname": "worker-01",
        "hostIP"  : "10.20.111.2"
    },
    {
        "hostname": "worker-02",
        "hostIP"  : "10.20.111.5"
    },
    {
        "hostname": "worker-03",
        "hostIP"  : "10.20.111.6"
    },
    {
        "hostname": "worker-04",
        "hostIP"  : "10.20.111.7"
    },
    {
        "hostname": "worker-05",
        "hostIP"  : "10.20.111.3"
    },
    {
        "hostname": "worker-06",
        "hostIP"  : "10.20.111.4"
    },
    {
        "hostname": "worker-07",
        "hostIP"  : "10.20.111.8"
    },
    {
        "hostname": "worker-08",
        "hostIP"  : "10.20.111.9"
    },
    {
        "hostname": "worker-09",
        "hostIP"  : "10.20.111.10"
    },
    {
        "hostname": "worker-10",
        "hostIP"  : "10.20.111.11"
    }
]


# HOSTNAME = "worker-06"
# HOSTIP   = "10.20.111.4"
USER     = 'expeca'
PSW      = 'expeca'
# SSHKEY   = '/home/expeca/.ssh/id_rsa'



def main():

    # Start expeca-exporter locally

    try:
        result = subprocess.check_output(['ps','-ax'])
        bytelinelist = result.splitlines()
    except:
        print("Controller: process check failed")

    linelist = []
    for byteline in bytelinelist:
        linelist.append(byteline.decode())

    exporter_active = False
    for line in linelist:
        if "expeca-exporter.py" in line:
            exporter_active = True

    if exporter_active:
        print("Controller: expeca-exporter is already active")
    else:
        try:
            result = subprocess.Popen(['python3','/home/expeca/exporter/expeca-exporter.py'])
            print("Controller: expeca-exporter restart done")
        except:
            print("Controller: expeca-exporter restart failed")


    # for host_item in host_list:

    #     HOSTNAME = host_item["hostname"]
    #     HOSTIP   = host_item["hostIP"]

    #     client = paramiko.SSHClient()
    #     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     # pkey = paramiko.RSAKey.from_private_key_file(SSHKEY)
    #     # client.connect(hostname=HOSTIP, disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}, username=USER, pkey=pkey)

    #     try:
    #         client.connect(hostname=HOSTIP, username=USER, password=PSW)
    #         connect_ok = True
    #     except:
    #         connect_ok = False
    #         print(HOSTNAME + ": Connect failed")

    #     if connect_ok:
    #         try:
    #             command = "ps -ax | grep 'node_exporter'"
    #             stdin, stdout, stderr = client.exec_command(command)              # Check process in worker node
    #             bytelinelist = stdout.read().splitlines()                         # Collect command output

    #             if len(bytelinelist) < 3:                                         # If node_exporter process is not executing
    #                 command = "/home/expeca/exporter/node_exporter-1.5.0.linux-amd64/node_exporter &"
    #                 stdin, stdout, stderr = client.exec_command(command)              # Start node_exporter
    #                 print(HOSTNAME + ": node_exporter restart done")
    #             else:
    #                 print(HOSTNAME + ": node_exporter is already active")
    #         except:
    #             print(HOSTNAME + ": node_exporter restart failed")


    return



if __name__ == "__main__":
    main()


