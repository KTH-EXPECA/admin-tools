#!/usr/bin/env python
# Run this on mgmt router:
# wget https://raw.githubusercontent.com/KTH-EXPECA/admin-tools/main/scan.py
# python scan.py

import socket
import subprocess
import sys
from datetime import datetime

# Define hosts to scan
hosts = {
    'mgmt-switch-01.expeca' : {
        'port' : 80
    },
    'tenant-switch-01.expeca' : {
        'port' : 22
    },
    'ptp-switch-01.expeca' : {
        'port' : 22
    },
    'ptp-clock.expeca' : {
        'port' : 22
    },
    'storage-01.expeca' : {
        'port' : 22
    },
    'storage-01-ipmi.expeca' : {
        'port' : 22
    },
    'controller-01.expeca' : {
        'port' : 22
    },
    'worker-01.expeca' : {
        'port' : 22
    },
    'worker-01-ipmi.expeca' : {
        'port' : 22
    },
    'worker-02.expeca' : {
        'port' : 22
    },
    'worker-02-ipmi.expeca' : {
        'port' : 22
    },
    'worker-03.expeca' : {
        'port' : 22
    },
    'worker-03-ipmi.expeca' : {
        'port' : 22
    },
    'worker-04.expeca' : {
        'port' : 22
    },
    'worker-04-ipmi.expeca' : {
        'port' : 22
    },
    'worker-05.expeca' : {
        'port' : 22
    },
    'worker-05-ipmi.expeca' : {
        'port' : 22
    },
    'worker-06.expeca' : {
        'port' : 22
    },
    'worker-06-ipmi.expeca' : {
        'port' : 22
    },
    'worker-07.expeca' : {
        'port' : 22
    },
    'worker-07-ipmi.expeca' : {
        'port' : 22
    },
    'worker-08.expeca' : {
        'port' : 22
    },
    'worker-08-ipmi.expeca' : {
        'port' : 22
    },
    'worker-09.expeca' : {
        'port' : 22
    },
    'worker-09-ipmi.expeca' : {
        'port' : 22
    },
    'worker-10.expeca' : {
        'port' : 22
    },
    'worker-10-ipmi.expeca' : {
        'port' : 22
    },
    'poe-switch-01.expeca' : {
        'port' : 80
    },
    'poe-switch-02.expeca' : {
        'port' : 80
    },
    'sdr-01-ni.expeca' : {       
        'port' : 22              
    },                           
    'sdr-01-mango.expeca' : {     
        'port' : 22              
    },                           
    'sdr-02-ni.expeca' : {       
        'port' : 22              
    },                           
    'sdr-02-mango.expeca' : {     
        'port' : 22           
    },                        
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
