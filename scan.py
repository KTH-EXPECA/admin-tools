#!/usr/bin/env python
# Run this on mgmt router:
# curl -LJO https://raw.githubusercontent.com/KTH-EXPECA/admin-tools/main/all.json
# curl -LJO https://raw.githubusercontent.com/KTH-EXPECA/admin-tools/main/scan.py
# JSON_PATH=all.json python scan.py

import os
import socket
import subprocess
import sys
from datetime import datetime
import json


def check_host(name,server_ip,port):
    print("-" * 90)

    # We also put in some error handling for catching errors             
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((server_ip, port))
        sock.close()
        if result == 0:
            resStr = 'Up'
        else:
            resStr = 'Down'

    except KeyboardInterrupt:
        print("You pressed Ctrl+C")
        sys.exit()
    except socket.error:
        print("Couldn't connect to server")
        sys.exit()

    print("{:<30} {:<20} {:<10} {:<20}".format(name,server_ip,port,resStr))

# open json
json_path = os.environ['JSON_PATH']
with open(json_path) as json_file:
    hosts = json.load(json_file)

# Print a nice banner with information on which host we are about to scan
print("-" * 90)
print("{:<30} {:<20} {:<10} {:<20}".format('HOST','IP','PORT','STATUS'))

for host in hosts:

    if "ip" in list(hosts[host].keys()):
        server_ip = hosts[host]['ip']
        port = int(hosts[host]['port'])
        check_host(host,server_ip,port)
    else:
        for subhost in hosts[host]:
            server_ip = hosts[host][subhost]['ip']
            port = int(hosts[host][subhost]['port'])
            check_host(host+"-"+subhost,server_ip,port)


print("-" * 90)
