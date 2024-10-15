#!/usr/bin/env python
# install paramiko package: pip3 install paramiko
# Make sure the following entries are in /etc/hosts:
# 10.20.111.1 storage-01
# 10.20.111.2 worker-01
# 10.20.111.5 worker-02
# 10.20.111.6 worker-03
# 10.20.111.7 worker-04
# 10.20.111.3 worker-05
# 10.20.111.4 worker-06
# 10.20.111.8 worker-07
# 10.20.111.9 worker-08
# 10.20.111.10 worker-09
# 10.20.111.11 worker-10
# Run this on openstack controller:
# curl -LJO https://raw.githubusercontent.com/KTH-EXPECA/admin-tools/main/scan-internal.py
# python3 scan-control.py

import socket
import subprocess
import sys
import paramiko
from datetime import datetime
import json
import os


os.chdir(sys.path[0])      # Set current directory to script directory


USER = 'expeca'
SSHKEY = '/home/expeca/.ssh/id_rsa'

# Define hosts to scan
hosts = {
    'storage-01' : {
        'port' : 22
    },
    'worker-01' : {
        'port' : 22
    },
    'worker-02' : {
        'port' : 22
    },
    'worker-03' : {
        'port' : 22
    },
    'worker-04' : {
        'port' : 22
    },
    'worker-05' : {
        'port' : 22
    },
    'worker-06' : {
        'port' : 22
    },
    'worker-07' : {
        'port' : 22
    },
    'worker-08' : {
        'port' : 22
    },
    'worker-09' : {
        'port' : 22
    },
    'worker-10' : {
        'port' : 22
    }                       
}                             


def main():

    # Print a nice banner with information on which host we are about to scan
    # print("-" * 100)
    # print ("{:<20} {:<20} {:<10} {:<10} {:<15} {:<20}".format('HOST','IP','PORT','STATUS','SSH', 'PASSWORD'))

    outp_list = []

    for host in hosts:
        remoteServer = host
        port = hosts[host]['port']

        try:
            remoteServerIP = socket.gethostbyname(remoteServer)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((remoteServerIP, port))
            sock.close()

            if result == 0:
                resStr = 'Up'
            else:
                resStr = 'Down'

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            pkey = paramiko.RSAKey.from_private_key_file(SSHKEY)

            try:
                ssh.connect(
                    remoteServerIP,
                    username=USER,
                    pkey=pkey,
                    timeout=10,
                    disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}
                )
                resStrSSH = 'Success'

                try:
                    stdin, stdout, stderr = ssh.exec_command("sudo -n true", timeout=5)
                    result = stdout.channel.recv_exit_status()

                    if result == 0:
                        resStrSUDO = 'is passwordless'
                    else:
                        resStrSUDO = 'needs a password'
                except socket.timeout:
                    resStrSUDO = 'SUDO command timed out'
                except Exception as e:
                    resStrSUDO = f'SUDO command failed: {str(e)}'

            except (paramiko.ssh_exception.BadHostKeyException,
                    paramiko.ssh_exception.AuthenticationException,
                    paramiko.ssh_exception.SSHException,
                    socket.timeout) as e:
                resStrSSH = 'Fail'
                resStrSUDO = '-'

        except KeyboardInterrupt:
            print("You pressed Ctrl+C")
            sys.exit()
        except socket.gaierror:
            remoteServerIP = '-'
            resStr = 'Hostname not found'
            resStrSSH = '-'
            resStrSUDO = '-'
        except socket.timeout:
            remoteServerIP = '-'
            resStr = 'Connection timed out'
            resStrSSH = '-'
            resStrSUDO = '-'
        except Exception as e:
            remoteServerIP = '-'
            resStr = f'Error: {str(e)}'
            resStrSSH = '-'
            resStrSUDO = '-'

        status = 1 if resStr == "Up" else 0

        outp = {
            "metric_name": "expeca_server_status",
            "labels": {
                "remoteServer": remoteServer,
                "remoteServerIP": remoteServerIP,
                "port": port,
                "resStr": resStr,
                "resStrSSH": resStrSSH,
                "resStrSUDO": resStrSUDO
            },
            "value": status
        }

        outp_list.append(outp)

    print(json.dumps(outp_list, indent=4))


if __name__ == "__main__":
    main()
