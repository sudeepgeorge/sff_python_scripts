# This script implements the SFF CLI interface on the host PC.

from socket import *
from struct import *
from time import *
from string import *
import sys
import socket
import os
import getpass
import select

#Change these IP address according to the host IP and board IP
HOST='172.16.0.140'
HOST_PORT= 49166

TARGET='172.16.0.19'
TARGET_PORT=49177

COMMAND_CANCEL   =     5
COMMAND_FILE_TR  =     55
COMMAND_RESPONSE =     20
COMMAND_CLI_HELP =     1

CLI_COMMAND_PACKET      =1
CLI_COMMAND_SUCCEEDED   =2
CLI_COMMAND_FAILED      =3
CLI_GET_PASSWORD        =4
CLI_TAKE_PASSWORD       =5
CLI_READY4_CONNECT      =6
CLI_READY4_ARGS         =7
CLI_GET_SIGN            =8
CLI_TAKE_SIGN           =9
CLI_GET_USERNAME        =10
CLI_TAKE_USERNAME        =11



COMMAND_PACKET_MAGIC    =0xacad1ac0
DATA_PACKET_MAGIC       =0xacad1ada
MAGIC_LEN               =8
COMMAND_LEN             =20

commandNum=0

#***************************************************************
#This function is used to split a string into arguments.
#It will separate arguments on the basis of spaces,
#if the string contains a substring made up of multiple space
#separated elements, it will consider it as a single argument
#For e.g the string:
#"this is a test string "containing a substring" ."
#consists of 7 arguments - 
#['this','is','a','test','string','containing a substring','.']


#Shamelessly picked 'split_args' from
#comp.lang.python.Thanks Mr.Fred Gansevles.

#params:s, quote = '"'

#param s:
# This is the input string

#param quote
#The separator on which the string is split into arguments,
#defaults to spaces

#return
#A list containing the arguments
#***************************************************************

def split_args(s, quote = '"'):
      ret = []
      qclose = 0      #closing quote
      q = find (s, quote)
      while q >= 0:
          if qclose:
              ret.append (s[:q])
              qclose = 0
          else:
              map (ret.append, split (s[:q]))
              qclose = 1
          s = s[q+1:]
          q = find (s, quote)
      map (ret.append, split (s))
      return ret 


#***************************************************************
#This function will connect to the target, the target IP addr
#and Port are global variables

#params: None

#return: Connected socket file descriptor or 0
#***************************************************************
def ServerConnect():
    global client_sock
    client_sock=0
    connect_result=0
    try:
      client_sock=socket.socket(AF_INET,SOCK_STREAM)
    except:
      print "Connection issue with the host machine."
      print "Please reboot the host machine and the SFF board."
      return 0
    
    try:
      connect_result=client_sock.connect_ex((TARGET,TARGET_PORT))
        
      if(connect_result!=0):
            print "\nCLI has lost connection to the board."
            return 0
        
      client_sock.settimeout(10.0)
        
      response=client_sock.recv(2048)
      if response==0:
            return 0
      
      try:
            command_response=unpack('!Iiiii',response)
            print command_response
            if command_response[0]==COMMAND_PACKET_MAGIC:
                  if command_response[1]==CLI_READY4_CONNECT:
                        return client_sock
                  else:
                        return 0
            else:
                  return 0
            
      except:
            print "Unexpected error:", sys.exc_info()[0]
            raise

      
    except(socket.timeout):
      print "\nCannot connect to the SFF Board."
      return 0             
    except socket.error:
      print "\nCannot connect to the SFF Board."
      return 0     
    except KeyboardInterrupt:
      print "\nUser has closed the CLI."
      return 0
   
    
#*******************************************************************************
#This function will send the command to the target board, the
#protocol used is briefly mentioned here,for further details
#look into the SFF design documents
#
#The structure of the command packet is as follows;
#Tag                   Size            Description
#--------------        ----------      -------------------------------------
#Command Header        4 Bytes         Contain magic # 0xACAD1AC0.
#Command ID            4 Bytes         Command number.
#Command Number        4 Bytes         command sequence (not used)
#Command Length        4 Bytes         length of command packet. 
#Argument Count        4 Bytes         It will contain the number of the 
#                                      arguments for a command. The arguments,
#                                      if any, are to be transmitted subsequent
#                                      to a command packet using a data packet
#                                      for each argument. 
#                                      
# If there are arguments, send them.
# Send the argument in data packets, one per arg.
#             |-------------------|----------------|----------|
# pkt format: |MAGIC # (4 bytes)  | LEN (4 bytes)  | DATA ... |
#             |-------------------|----------------|----------|
#

#params: argc,argv

#param argc: The number of arguments

#param argv: The list of arguments

#return: 0 if all OK else 1
#*******************************************************************************

def SendCmd(argc, argv):
      global commandNum
      global client_sock
      commandNum+=1
      command=pack('!IIIII',COMMAND_PACKET_MAGIC,CLI_COMMAND_PACKET,commandNum,0,(argc))
      client_sock.send(command)
      
      if argc >= 1:
      
        for i in range(0, argc):
            pktLen = len(argv[i]) + 1
            fmtStr = '!II%ds' % int(pktLen)
            dataPkt=pack(fmtStr,DATA_PACKET_MAGIC,pktLen,argv[i])
            try:
                client_sock.send(dataPkt)
            except (socket.error):
                print "\n The network connection to the SFF Board is lost."
                print "Please try after 15 seconds."
                print "Bye."
                return 1
            
       

      client_sock.settimeout(1.0)
      repeatCount = 0
      
      data_len_needed = MAGIC_LEN
      data=""
      
      
      while 1:
        
        try:
            data += client_sock.recv(data_len_needed)
            
            rcvd_data_len=len(data)
            
            if (rcvd_data_len<=0):
                print 'The SFF Board has closed the connection'
                print 'Bye'
                return 1
            
            if rcvd_data_len<data_len_needed:
                  data_len_needed-=rcvd_data_len
                  continue
            
            peek_header=unpack('!Ii',data)

            
            if (peek_header[0]==DATA_PACKET_MAGIC):
                  expected_pack_len=peek_header[1]
                  data=""
                  
                  if repeatCount:
                        print
                        
                  packet_data = client_sock.recv(expected_pack_len)
                  if not packet_data:
                        print 'The SFF Board has closed the connection'
                        print 'Bye'
                        return 1
                  
                  rcvd_data_len=len(packet_data)
                  
                  if expected_pack_len<=rcvd_data_len:
                        print packet_data,
                        data_len_needed=MAGIC_LEN
                        continue
                        
                  else:
                        data_len_needed=expected_pack_len-rcvd_data_len
                        while 1:
                              print packet_data,
                              packet_data=client_sock.recv(data_len_needed)
                              if not packet_data:
                                print 'The SFF Board has closed the connection'
                                print 'Bye'
                                return 1
                            
                              rcvd_data_len=len(packet_data)
                                                          
                              if rcvd_data_len>=data_len_needed:
                                print packet_data,
                                data_len_needed=MAGIC_LEN
                                break
                              else:
                               print packet_data,
                               data_len_needed-=rcvd_data_len
                               continue
                  
            elif(peek_header[0]==COMMAND_PACKET_MAGIC):
                  command_packet=""
                  data=""
                  reqd_command_len=COMMAND_LEN-MAGIC_LEN
                  rcvd_command_len=0
                  while 1:
                        command_packet += client_sock.recv(reqd_command_len)
                        rcvd_command_len=len(command_packet)
      
                        if (rcvd_command_len<=0):
                            print 'The SFF Board has closed the connection'
                            print 'Bye'
                            return 1
                        
                        if rcvd_command_len<reqd_command_len:
                              reqd_command_len-=rcvd_command_len
                              continue
                        
                        command=unpack('!iii',command_packet)
                        break
                  
                  if peek_header[1]==CLI_COMMAND_SUCCEEDED:
                        print "The command succeeded."
                        return 0
                  elif peek_header[1]==CLI_COMMAND_FAILED:
                        print "The command failed."
                        return 0
                  elif peek_header[1]==CLI_GET_USERNAME:
                  	if(command[0]!=commandNum):
			      print "CLI has received an invalid response from the Board"
                              break
                              
                        print "\nPlease enter the username to continue with the firmware update."      
                        while 1:
                          try:
                              username =  raw_input("Username:")
                              if(username is not ""):
                                  break
                          except KeyboardInterrupt:
                              print "\nUser has closed the CLI."
                              print "Bye."
                              return 1
                        
                        username_comm_resp=pack('!IIIII',COMMAND_PACKET_MAGIC,CLI_TAKE_USERNAME,commandNum,0,0)
                        client_sock.send(username_comm_resp)
                                                
                        fmtStr = '!II%ds' %(len(username)+1)
                        user_name=pack(fmtStr,DATA_PACKET_MAGIC,(len(username)+1),username)
                        client_sock.send(user_name)                          
                         
                  elif peek_header[1]==CLI_GET_PASSWORD:
                        if(command[0]!=commandNum):
                              print "CLI has received an invalid response from the Board"
                              break
                        
                        print "\nPlease enter the password to continue with the firmware update."
                        while 1:
                          try:
                              passwd =  getpass.getpass("Password:")
                              if(passwd is not ""):
                                  break
                          except KeyboardInterrupt:
                              print "\nUser has closed the CLI."
                              print "Bye."
                              return 1
                        
                        password_comm_resp=pack('!IIIII',COMMAND_PACKET_MAGIC,CLI_TAKE_PASSWORD,commandNum,0,0)
                        client_sock.send(password_comm_resp)
                                                
                        fmtStr = '!II%ds' %(len(passwd)+1)
                        user_password=pack(fmtStr,DATA_PACKET_MAGIC,(len(passwd)+1),passwd)
                        client_sock.send(user_password)
                  
                  elif peek_header[1]==CLI_GET_SIGN:
                        if(command[0]!=commandNum):
                              print "CLI has received an invalid response from the Board"
                              break
                        
                        print "\nPlease enter the signature to continue with the firmware update."
                        while 1:
                          try:
                              sign =  raw_input("Signature:")
                              if(sign is not ""):
                                  break
                          except KeyboardInterrupt:
                              print "\nUser has closed the CLI."
                              print "Bye."
                              return 1
                        
                        sign_comm_resp=pack('!IIIII',COMMAND_PACKET_MAGIC,CLI_TAKE_SIGN,commandNum,0,0)
                        client_sock.send(sign_comm_resp)
                                                
                        fmtStr = '!II%ds' %(len(sign)+1)
                        signature=pack(fmtStr,DATA_PACKET_MAGIC,(len(sign)+1),sign)
                        client_sock.send(signature)                         
                  else:
                       print "CLI has received an invalid response from the Board"
                       break
            
            else:
                  print "CLI has received an invalid response from the Board"
                  break
           
        except KeyboardInterrupt:
            print "\nUser has closed the CLI."
            print "Bye."
            return 1

        except(socket.timeout):
            if(repeatCount==0):
                print ""
            print '*',
            repeatCount += 1
            if (repeatCount%40==0 and repeatCount>2):
                print "\r"
            
            
            if(repeatCount > 300):
                print "\nData not received or received incorrectly. Exiting this command."
                return 1
         
            
        except (socket.error):
            print "\n The network connection to the SFF Board is closed."
            print "Please try after 15 seconds."
            print "Bye."
            return 1
        
      client_sock.settimeout(None)
      return 0

#*******************************************************************************
#The main module which does it all,
# Sets up the connections, and executes the user entered commands
#*******************************************************************************
if __name__=='__main__':
#Print the header
    print "\n"
    print "\n"
    print "*"*57
    print "*\t Acadia Small Form Factor CLI V0.9\t\t*"
    print "*"*57
    print "\n"
    print "- Type help at the prompt for a list of commands."
    print "- Type exit at the prompt to quit the CLI."
    print "- Type Ctrl-C to break out of the CLI."
    print "\n"
    
    
    os.system('title SFF-CLI') 

    global client_sock
    passwd_recvd=0

    while 1:
        try:
            returnVal = ServerConnect()
            break;
        except KeyboardInterrupt:
            print"\nUser has closed the CLI."
            print "Bye."
            raw_input('\nPress any key to close.')
            sys.exit(0)
        
        
    if returnVal <= 0:
        print '\nError connecting to the Target Board.',TARGET
        print 'CLI exiting. Bye.'
        raw_input('\nPress any key to close.') 
        sys.exit(1)
    
    print "Connected to the board"    
    
    while 1:
        
      try:
            valStr = raw_input("\n[SFF-CLI]# ")
            if valStr == '':
                continue
    
  
            argv = split(valStr)
            if (argv[0] == '100'  or  argv[0] == 'Exit'  or  argv[0] == 'exit'):
                print "Exiting the CLI."
                print "Bye."
                break;
            
            #if( argv[0]=='filetransfer'):                
            #    print "\nPlease enter the password to continue with the firmware update."
            #    while 1:
            #        try:
            #            passwd =  getpass.getpass("Password:")
            #            passwd_recvd=1
            #            if(passwd is not ""):
            #                break
            #        except KeyboardInterrupt:
            #            print "\nUser has closed the CLI."
            #            print "Bye."
            #            client_sock.shutdown(SHUT_RDWR)
            #            client_sock.close()
            #            raw_input('\nPress any key to close.')
            #            sys.exit(0)

        
            argv=split_args(valStr)

            if(len(argv)==0):
                continue
            
         
             
            if(passwd_recvd==1):
                if(len(argv)>2):
                    filename=argv[2]
                    argv[2]=passwd
                    argv.append(filename)
                else:
                    argv.append(passwd)
                    
                passwd_recvd=0
                    
            argc = len(argv)
            print " ",
            cmdreturn=SendCmd(argc, argv)
            if cmdreturn!=0:
                break

      except KeyboardInterrupt: #Ctrl-C 
            print "\nUser has closed the CLI."
            print "Bye."
            break
      
      except EOFError: # Ctrl-Z
            print "\nUser has closed the CLI."
            print "Bye."
            break

    client_sock.shutdown(SHUT_RDWR)
    client_sock.close()
    try:
      raw_input('\nPress any key to close.')
    except:#catch-all
      pass
    sys.exit(0)


