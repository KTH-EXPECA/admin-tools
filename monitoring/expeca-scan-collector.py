#!/usr/bin/env python
#
import sys
import os
import json
import paramiko


os.chdir(sys.path[0])      # Set current directory to script directory

HOST = "10.10.1.1"
USER = 'expeca'
SSHKEY = '/home/expeca/.ssh/id_rsa'


def main():

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


    outp_list = []

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
                                                         
    print(json.dumps(outp_list, indent = 4))

    return



if __name__ == "__main__":
    main()

