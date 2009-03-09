import os
import sys
import struct

#See the 'WindRiver ICE Binary File Format.pdf' for
#details on the file format.

# Header for the ICE Binary file

#8-Byte Ascii header.
header1=['E','S','T','F','B','I','N','R']
# Starting and Ending Address
header2=[0,0,0,0,0,0,0,6]
#Fill character,Reserved Bytes,Actual addr[start and end]
header3=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,6]


#SARNOFF MAC address range for the SFF Boards - 
# 00-E0-9D-FF-FE-0C to 00-E0-9D-FF-FF-FF



#MAC Address to be written now
Mac_Addr=[0x0,0xe0,0x9d,0xff,0xfe,0x0c]

def EST_Header(bin_fd):
    for i in header1:
        data=struct.pack('c',i)
        bin_fd.write(data)
        
    for i in header2:
        data=struct.pack('B',i)
        bin_fd.write(data)
    
        
        
    for i in header3:
        data=struct.pack('B',i)
        bin_fd.write(data)

  
def write_bin_data(bin_fd,data):
    for i in data:
        byte=struct.pack('B',i)
        bin_fd.write(byte)

if __name__=='__main__':
    
    #create the Bin file to hold the MAC Address
    try:
        bin_fd=open("MacWRICE.bin",'wb')
    except:
        print 'Unable to create the binary file '
        print sys.exc_value
        raw_input("Press any key to exit")
        sys.exit(1)   
        
    #create the header
    EST_Header(bin_fd)
    
    #Write the MAC address    
    write_bin_data(bin_fd,Mac_Addr)
    
    bin_fd.close()
        
    

    
