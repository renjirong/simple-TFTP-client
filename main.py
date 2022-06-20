import socket
import header
import os
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
ADDR = input("Enter TFTP server IP address: ") #"192.168.0.161" 
PORT = int(input("Enter TFTP server PORT number: ")) #69
TFTPserver = (ADDR, PORT)
# FileName = b"FileA.jpg"
choice = int(input("RRQ = 1 WRQ = 2: "))
FileName = input("Input File Name: ") #"FileB.bin"
FileName_byte = str.encode(FileName)
UDPClientSocket.settimeout(5)
try:
    if choice == 1:
        RRQobj = header.RRQ(UDPClientSocket, FileName, TFTPserver)
        RRQobj.sendRRQ()
        RRQobj.startRRQ()
        port = RRQobj.getPort()
        print("SUCCESS")
        print("PORT: " + str(port))
    else:
        if os.path.isfile(FileName):
            WRQobj = header.WRQ(UDPClientSocket, FileName, TFTPserver)
            WRQobj.sendWRQ()
            WRQobj.startWRQ()
            port = WRQobj.getPort()
            print("SUCCESS")
            print("PORT: " + str(port))
        else:
            print("Local: File not found")
except Exception as e:
    print(e)
except socket.timeout:
    print("timedout")
UDPClientSocket.close()

