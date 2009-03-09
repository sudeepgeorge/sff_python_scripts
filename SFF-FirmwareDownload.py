#This script file is used to update the
#firmware on the SFF Board

from socket import *
from struct import *
from time import *
from string import *
import sys
import socket
import getpass
import os

#Change these IP address according to the host IP and board IP
HOST='172.16.0.102'
HOST_PORT= 49199

TARGET='172.16.1.41'
TARGET_PORT=49188

#*******************************************************************************
#This module is used to connect to the SFF board,
#performing the required authentication

#params: None

#return: 0 if error,else the socket file descriptor
#*******************************************************************************
def ServerConnectandAuth():
    global client_sock
    client_sock=0
    repeatCount=0
    username_stage=0
    password_stage=0
    signature_stage=0
    
    print "Please wait while the connection to the board is being established."

    try:
        client_sock=socket.socket(AF_INET,SOCK_STREAM)
    except:
        print "Connection issue with the host machine."
        print "Please reboot the host machine and the SFF board."
        raw_input('\nPress any key to close.')
        sys.exit(0)
    
 
    while 1:
        try:
            client_sock.connect((TARGET,TARGET_PORT))
            break           
        except KeyboardInterrupt:
            print "\nUser has closed the firmware upgrade utility."
            print "Bye."
            raw_input('\nPress any key to close.') 
            sys.exit(0)
        except(repeatCount==80):
            print "\nCannot connect to the target board."
            print "Bye."
            raw_input('\nPress any key to close.') 
            sys.exit(0)        
        except socket.error:
            if(repeatCount==0):
                 print ""
            if (repeatCount%40==0 and repeatCount>2):
                 print "\r"
            repeatCount += 1
            print '*',
            continue
    
    while 1:
  
        try:
            data = client_sock.recv(2048)
        except:
            print "\nUnable to communicate with the board."
            print "Please reboot the SFF board."
            raw_input('\nPress any key to close.') 
            sys.exit(0)
            
            
            
        if data.find("username")>=0:
            
            print "\nPlease enter the username to continue with the firmware update."
            while 1:
                try:
                    username =  raw_input("Username:")
		    if(username is not ""):
                        break
                except KeyboardInterrupt:
                   print "\nUser has closed the firmware upgrade utility."
                   print "Bye."
                   raw_input('\nPress any key to close.') 
                   sys.exit(0)
                except:
                    print "\nUnable to communicate with the board."
                    print "Bye."
                    raw_input('\nPress any key to close.') 
                    sys.exit(0)
                    
            
            try:
                client_sock.send(username)
            except:
                print "\nUnable to communicate with the board."
                print "Please reboot the SFF board."
                raw_input('\nPress any key to close.') 
                sys.exit(0)
                
            username_stage=1
            
        elif data.find("password")>=0:
            username_stage=0
            print "\nPlease enter the password to continue with the firmware update."
            while 1:
                try:
                    passwd =  getpass.getpass("Password:")
                    if(passwd is not ""):
                        break
                except KeyboardInterrupt:
                   print "\nUser has closed the firmware upgrade utility."
                   print "Bye."
                   raw_input('\nPress any key to close.') 
                   sys.exit(0)
                except:
                    print "\nUnable to communicate with the board."
                    print "Bye."
                    raw_input('\nPress any key to close.') 
                    sys.exit(0)
                    
            
            try:
                client_sock.send(passwd)
            except:
                print "\nUnable to communicate with the board."
                print "Please reboot the SFF board."
                raw_input('\nPress any key to close.') 
                sys.exit(0)
                
            password_stage=1
       
        elif data.find("Signature")>=0:
        
            password_stage=0
            print "\nPlease enter the signature to continue with the firmware update."
            while 1:
                try:
                    signature =  raw_input("Signature:")
                    if(signature is not ""):
                        break
                except KeyboardInterrupt:
                   print "\nUser has closed the firmware upgrade utility."
                   print "Bye."
                   raw_input('\nPress any key to close.') 
                   sys.exit(0)
                except:
                    print "\nUnable to communicate with the board."
                    print "Bye."
                    raw_input('\nPress any key to close.') 
                    sys.exit(0)
            
            try:
                client_sock.send(signature)
            except:
                print "\nUnable to communicate with the board."
                print "Please reboot the SFF board."
                raw_input('\nPress any key to close.') 
                sys.exit(0)
            
            signature_stage=1
            
        elif data.find("okay")>=0:            
            if password_stage==1:
                print "Password sent successfully to the board." 
            elif username_stage == 1:
            	print "Username sent successfully to the board."
            elif signature_stage==1:
                print "The signature was accepted."
                return client_sock
            else:
                print data
                
        elif data.find("Error")>=0:
            if username_stage==1:
	        print "Username could not be received successfully by the SFF board."        
	        print "Please reboot the SFF board."
	        raw_input('\nPress any key to close.') 
                sys.exit(0)
            elif password_stage==1:
                print "Password could not be received successfully by the SFF board."        
                print "Please reboot the SFF board."
                raw_input('\nPress any key to close.') 
                sys.exit(0)
            elif signature_stage==1:
                print "The signature was not accepted. "        
                print "Please reboot the SFF board."
                raw_input('\nPress any key to close.') 
                sys.exit(0)
            else:
                print data
                
                
    
#*******************************************************************************
#This module does it all, connects to the SFF board,
#sends the download command and verifies the result of the firmware
#update process
#*******************************************************************************
    
if __name__=='__main__':
    global client_sock
#Print the header
    print "\n"
    print "\n"
    print "*"*57
    print "* Acadia Small Form Factor Firmware Update Utility V0.9\t*"
    print "*"*57
    print "\n"


    os.system('title SFF-FirmwareDownload') 
    
    download_started=0
    while 1:
        try:
            returnVal = ServerConnectandAuth()
            if returnVal == 0:
                print '\nError connecting to the Target Board.',TARGET
                print 'Retrying the connection.'
                continue
            else:
                break
        except KeyboardInterrupt:
            print"\nUser has closed the firmware upgrade utility."
            print "Bye."
            raw_input('\nPress any key to close.') 
            sys.exit(0)
    
    print "\n"
    print "\n"
    print "- Type exit at the prompt to quit the firmware upgrade utility."
    print "- Type Ctrl-C to break out of the firmware upgrade utility."
    print "\n"
    
    print 'Enter the name of the new firmware file.'
    while (download_started==0):
        try:
            valStr =  raw_input("\n[SFF-FirmwareUpdate]#")
            valStr = valStr + '\0'
            if valStr == '':
                continue
                
    	    
            argv = split(valStr)
                        
            if (argv[0] == '100'  or  argv[0] == 'Exit'  or  argv[0] == 'exit'):
                print "If the download process is in progress, it will continue in the background."
                print "Please reboot and check the firmware after 5 minutes."
                print "Bye."
                raw_input('\nPress any key to close.')                  
                sys.exit(0)                

            elif (argv[0]!=""):            	
                download_started=1                
                break
                       
            else:                
                continue
            
          
        except KeyboardInterrupt:
            print "\nUser has closed the firmware upgrade utility."
            print "Bye."
            raw_input('\nPress any key to close.') 
            sys.exit(0)
        
    client_sock.send(argv[0])
    repeatCount=0
    client_sock.settimeout(1)
    while (download_started==1):
        try:
            data = client_sock.recv(2048)
            break

        except KeyboardInterrupt:
            print "\nUser has closed the firmware upgrade utility."
            print "If the download process is in progress, it will continue in the background."
            print "Please reboot and check the firmware after 30 seconds."            
            print "Bye."
            raw_input('\nPress any key to close.') 
            sys.exit(0)
        
        except socket.error:
            if(repeatCount==0):
                 print ""
            print '*',
            
            repeatCount += 1
            if (repeatCount%40==0 and repeatCount>2):
                print "\r"
            
            
            if(repeatCount > 150):
                print "\nData not received or received incorrectly. Exiting this command."
                raw_input('\nPress any key to close.') 
                sys.exit(1)    
            
    
    if (data=="Burn.okay"):
        print "\nThe firmware upgrade has completed successfully."
        print "Bye."
    else:
        print "\nThe firmware upgrade has failed."
        print "Please retry the process."
        print "Bye."
        
    client_sock.shutdown(SHUT_RDWR)
    client_sock.close()
    raw_input('\nPress any key to close.')
    sys.exit(0)


