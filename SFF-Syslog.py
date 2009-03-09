#!/usr/bin/env python
from socket import *
import sys
import string
from time import *
import time
import os

HOST=''
PORT=49144

#*******************************************************************************
#This module connects to the SFF Board, parses the messages as per
#protocol[see the SFF Design documents], prints the messages to the console
#and appends the log file.

#params: None

#result: None

#*******************************************************************************

def syslog_server():
	#If the directory does not exist, it needs to be created.
	filehandle=open('C:\SFF_Log\SYSLOG.txt','w')
	if not filehandle:
		print "Could not open the log file"
                print "Change the script if you need a Log file."
                print "Rerun the script after this change."
                sys.exit(-1)
                
        try:                
            serversock = socket(AF_INET,SOCK_DGRAM)
            serversock.bind((HOST,PORT))
        except:
            print "Host machine unable to setup connection."
            print "Consider rebooting the host machine."
	print "This log started at %s" %asctime()
	
        serversock.settimeout(5)
            
	while 1:
		try:
                    data=serversock.recv(1448)
                    if data.find("** ACADIA Small Form Factor Board")>0:
                        print "This session started at %s" %asctime()                        
                    print  data[9:]
                    print >> filehandle, data[9:]
                    filehandle.flush()
		except KeyboardInterrupt:
                    print"\nThe SFF syslog has been closed."
                    sys.exit(0)
                except:
                    continue    
	
		
#*******************************************************************************
#This is the main module
#*******************************************************************************

                
if __name__=='__main__':
    print "\n"
    print "\n"
    print "*"*57
    print "*\t Acadia Small Form Factor Syslog V1.0\t*"
    print "*"*57
    print "\n"
    print "- Type Ctrl-C to close the syslog."
    print "\n"
    
    os.system('title SFF-Syslog') 


    try:
        syslog_server()
    except KeyboardInterrupt:
        print "The SFF syslog has been closed."
        sys.exit(0)
        
    raw_input() 

