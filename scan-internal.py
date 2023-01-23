#!/usr/bin/env python
# Add the following entries to /etc/hosts
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
# python scan-control.py

import socket
import subprocess
import sys
from datetime import datetime

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
                              
# Print a nice banner with information on which host we are about to scan
print "-" * 90                                                           
print ("{:<30} {:<20} {:<10} {:<20}".format('HOST','IP','PORT','STATUS'))
                                                                         
for host in hosts:                                                       
    remoteServer = host                                                  
    port = hosts[host]['port']                                           
                                                                         
    print "-" * 90                                                       
                                                                         
    # We also put in some error handling for catching errors             
    try:                                                                 
        remoteServerIP  = socket.gethostbyname(remoteServer)             
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
        sock.settimeout(0.5)                                             
        result = sock.connect_ex((remoteServerIP, port))                 
        sock.close()                                                     
        if result == 0:                                                  
            resStr = 'Up'                                                
        else:                                                            
            resStr = 'Down'                                              
                                                                         
    except KeyboardInterrupt:                                            
        print "You pressed Ctrl+C"                                       
        sys.exit()        
    except socket.gaierror:                                              
        remoteServerIP = '-'                                             
        resStr = 'Hostname not found'                                    
                                                                         
    except socket.error:                                                 
        print "Couldn't connect to server"                               
        sys.exit()                                                       
                                                                         
    print ("{:<30} {:<20} {:<10} {:<20}".format(remoteServer,remoteServerIP,port,resStr))
                                                                                         
print "-" * 90
