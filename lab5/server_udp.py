import socket
import sys

HOST = '' #Symbolic name meaning all available interfaces
PORT = 8888

#datagram udp socket
try :
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print 'Socket Created!'
except socket.error, msg:
    print 'Failed to create socket. Error: ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()

#Bind socket to local host and port
try:
    s.bind((HOST,PORT))
except socket.error, msg:
    print "Bind failed. Error: " + srt(msg[0]) + " Message " + msg[1]
    sys.exit()

print "Socket Bind Complete"

#keep talking with client
while 1:
    #receive data from client (data, addr)
    d = s.recvfrom(1024)
    data = d[0]
    addr = d[1]

    if not data:
        break

    reply = "OK... " + data

    s.sendto(reply,addr)
    print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()

s.close()
