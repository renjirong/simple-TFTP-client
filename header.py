import os
import time

class header(object):
    def __init__(self):
        self.MODES = {
                'netascii' : b'netascii',
                'octet'    : b'octet'}

        self.OPCODES = {
                'RRQ'  : b'\x00\x01',  # RRQ
                'WRQ'  : b'\x00\x02',  # WRQ
                'DATA' : b'\x00\x03',  # DATA
                'ACK'  : b'\x00\x04',  # ACKNOWLEDGMENT
                'ERR'  : b'\x00\x05',  # ERROR
                'OACK' : b'\x00\x06'} # OACK

class RRQ(header):
    def __init__(self, UDPsocket, FileName, TFTPserver):
        header.__init__(self)
        self.TFTPserver = TFTPserver
        self.UDPsocket = UDPsocket
        self.FileName = FileName
    def  getPort(self):
        return self.TFTPserver[1]
    #SENDS AN RRQ AND ACK TO THE SERVER AND SETS TFTP PORT TO BE USED FOR FILE TRANSFERING 
    def sendRRQ(self): #RETURNS OACK
        self.UDPsocket.sendto(self.OPCODES["RRQ"] + str.encode(self.FileName) + b"\x00" + self.MODES["octet"] + b'\x00' + b"tsize\x000\x00",self.TFTPserver) #Read Request 
        data, addr = self.UDPsocket.recvfrom(516)#OACK
        OPCODE = data[:2]
        if OPCODE != self.OPCODES['OACK']:
            data1 = data[4:]
            print("Server: " + data1.decode('utf-8'))
            print("Exiting...")
            self.UDPsocket.close()
            exit(1)
        self.TFTPserver = addr
        self.UDPsocket.sendto(self.OPCODES["ACK"]+ b"\x00\x00",self.TFTPserver) #ACK BLOCK 0
        return data
        
    def startRRQ(self):
        with open("Download/" + self.FileName, "wb") as file:
            data, addr = self.UDPsocket.recvfrom(516) #recieve data block
            file.write(data[4:]) #Write File and Remove Header
            blk_num = data[2:4] #get data block number
            OPCODE = data[:2]   #get OPCODE from packet header
            while True:
                if len(data) < 512: #End Of File
                    blk_num = data[2:4]
                    self.UDPsocket.sendto(self.OPCODES["ACK"] + blk_num,self.TFTPserver) #Send Final ACK              
                    break
                self.UDPsocket.sendto(self.OPCODES["ACK"] + blk_num,self.TFTPserver) #ACK
                data, addr = self.UDPsocket.recvfrom(516) #recieve data block
                if OPCODE == self.OPCODES["DATA"]: #check if data packet is a DATA
                    if data[2:4] == blk_num: #Retry check if duplicate packet
                        print("Duplicate Packet Recieved")
                        t_end = time.time() + 5
                        while time.time() < t_end: #Retry for 5 seconds then exit program
                            print("Retrying")
                            data, addr = self.UDPsocket.recvfrom(516) #Receive Packet
                            if data[2:4] != blk_num:
                                break
                        if data[2:4] == blk_num:
                            self.UDPsocket.close()
                            print("TFTP Dupelicate Timedout")
                            exit(1)
                    file.write(data[4:]) #Write File and Remove Header
                    blk_num = data[2:4] #get data block number
                    OPCODE = data[:2]   #get OPCODE from packet header
                elif OPCODE == self.OPCODES["ERR"]:
                    data1 = data[4:]
                    print("Server: " + data1.decode('utf-8'))
                    break
        if OPCODE == self.OPCODES["ERR"]:
            os.remove("Download/" + self.FileName)
class WRQ(header):
    def __init__(self, UDPsocket, FileName, TFTPserver):
        header.__init__(self)
        self.TFTPserver = TFTPserver
        self.UDPsocket = UDPsocket
        self.FileName = FileName

    def  getPort(self):
        return self.TFTPserver[1]

    def sendWRQ(self): #RETURNS OACK
        self.UDPsocket.sendto(self.OPCODES["WRQ"] + str.encode("Upload/"+self.FileName) + b"\x00" + self.MODES["octet"] + b'\x00' + b"tsize\x000\x00",self.TFTPserver) #Read Request 
        
        data, addr = self.UDPsocket.recvfrom(516)#OACK
        OPCODE = data[:2]
        if OPCODE != self.OPCODES['OACK']:
            data1 = data[4:]
            print("Server: " + data1.decode('utf-8'))
            print("Exiting...")
            self.UDPsocket.close()
            exit(1)
        self.TFTPserver = addr
        return data
    
    def startWRQ(self):
        with open(self.FileName , "rb") as file:
            blk = 0
            while True:
                data = file.read(512)
                if not data:
                    if len(prevDat) == 512:
                        blk += 1  
                        blk_byte = int.to_bytes(blk, 2, "big")
                        self.UDPsocket.sendto(self.OPCODES["DATA"] + blk_byte + b"", self.TFTPserver)
                    break
                prevDat = data
                blk += 1  
                blk_byte = int.to_bytes(blk, 2, "big")
                
                self.UDPsocket.sendto(self.OPCODES["DATA"] + blk_byte + data, self.TFTPserver)
                data, addr = self.UDPsocket.recvfrom(516)
                OPCODE = data[:2]   #get OPCODE from packet header
                if OPCODE != self.OPCODES['ACK']:
                    break
        if OPCODE != self.OPCODES['ACK']:
            data1 = data[4:]
            print("Server: " + data1.decode('utf-8'))
            print("Exiting...")
            self.UDPsocket.close()
            exit(1)

