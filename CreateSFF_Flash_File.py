import os
import sys
import struct
import shutil
import stat
import os.path

#Default MAC Address to be written 
Mac_Addr=[0x0,0xe0,0x9d,0xff,0xfe,0x0c]

#Reset Configuration Word to be written
RCW=[0x04,0x23,0x0,0x0,0xA4,0x60,0xA0,0x02]

RCW_SIZE        =0x40
MAC_LOCATION    =0x10000
APP_LOCATION    =0xe0008
BOOT_LOCATION   =0x700100
FLASH_SIZE      =0x00800000


##############################################
def write_bin_rcw_data(bin_fd,data):
    for i in data:
        for j in range(8):
            byte=struct.pack('B',i)
            bin_fd.write(byte)

##############################################
def write_bin_data(bin_fd,data):
    for i in data:
        byte=struct.pack('B',i)
        bin_fd.write(byte)
 
##############################################        
def write_bin_filler(bin_fd,count):
    for i in range(count):
        byte=struct.pack('B',0xFF)
        bin_fd.write(byte)
        
##############################################        
def write_bin_app_file(bin_fd):
    try:
        app_fd=open("application",'rb')
        bin_fd.write(app_fd.read())
        app_fd.close()
    except:
        print 'Unable to open the application file '
        #print sys.exc_value
        raw_input("Press any key to exit")
        bin_fd.close()
        sys.exit(-1)
        
    


##############################################    
def write_bin_boot_file(bin_fd):
    try:
        boot_fd=open("bootrom",'rb')
        bin_fd.write(boot_fd.read())
        boot_fd.close()
    except:
        print 'Unable to open the bootrom file '
        #print sys.exc_value
        raw_input("Press any key to exit")
        bin_fd.close()
        sys.exit(-1)
        
      
    
    
    
    

if __name__=='__main__':
    
    
    print "\t",'*'*73
    print "\t",'*',"This script will create an 8MB file to be used to load the SFF flash.",'*'
    print "\t",'*',"This script will require an application file called 'application'.   ",'*'
    print "\t",'*',"This script will require a boot file called 'bootrom'.               ",'*'
    print "\t",'*',"Both these files need to be in the same directory as this script.    ",'*'
    print "\t",'*'*73
    print "\n\n"
    
    if not os.path.isfile('application'):
        print("The application file does not exist. Exiting.")
        sys.exit(-1)
        
    if not os.path.isfile('bootrom'):
        print("The bootrom file does not exist. Exiting.")
        sys.exit(-1)
        
    #create the Binary file
    try:
        bin_fd=open("SFF_Flash_File.bin",'wb')
    except:
        print 'Unable to create the binary file '
        print sys.exc_value
        raw_input("Press any key to exit")
        sys.exit(1)
        
    print("Starting to create the SFF_Flash_File.bin")        
    #counter to keep track of the file size    
    file_size=0
        
    #Write the RCW
    write_bin_rcw_data(bin_fd,RCW)
    
    #Write a filler for the space between RCW and MAC address
    write_bin_filler(bin_fd,(MAC_LOCATION-RCW_SIZE))
    
    file_size=bin_fd.tell()
    #print "MAC 0x%x" %file_size
        
    #Write the MAC address    
    write_bin_data(bin_fd,Mac_Addr)
    
    file_size=bin_fd.tell()
    
        
    #Write a filler for the space between MAC address and application file
    write_bin_filler(bin_fd,(APP_LOCATION-file_size))
    
    file_size=bin_fd.tell()
    #print "App 0x%x" %file_size
    
    #write the application
    write_bin_app_file(bin_fd)
    
    file_size=bin_fd.tell()
    #print "After App 0x%x" %file_size
    
    #Write a filler for the space between application file and bootrom file
    write_bin_filler(bin_fd,(BOOT_LOCATION-file_size))
    
    file_size=bin_fd.tell()
    #print "Boot 0x%x" %file_size
    
    write_bin_boot_file(bin_fd)
    
    file_size=bin_fd.tell()
    #print "After Boot 0x%x" %file_size
    
    #Write a filler for the space between bootrom file and EOF
    write_bin_filler(bin_fd,(FLASH_SIZE-file_size))
    
    file_size=bin_fd.tell()
    #print "EOF 0x%x" %file_size
    
    bin_fd.close()
    
    print "SFF_Flash_File.bin file created. Size:" , os.stat('SFF_Flash_File.bin')[stat.ST_SIZE]