import socket
import sys
from thread import *

HOST = ''   #Symbolic name meaning all available ineterfaces
PORT = 4367 #Arbitrary non-privilleged port

#Socket setup
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
print 'Socket created'

#Bind to Port
try:
    s.bind((HOST, PORT))
except socket.error, msg:
    print 'Bind failed. Error: ' + str(msg[0]) + ' Message ' + msg[1] + '\n'
    sys.exit()

print 'Socket bind complete'

#Listening
s.listen(5)
print 'Socket now Listening... '

clientList = []

#Function for handling connections. This will be used to create threads
def clientthread(conn):
    #Sending message to connected client
    conn.send('Welcome to the Darkside... Type something!\n')
    
    #infinite loop so that function do not terminate and thread do not end.
    while True:
        
        #Receiving from client
        data = conn.recv(1024)
        reply = 'ECHO: ' + data + '\n'
        
        if not data:
            break

        first_2_char = data[:2]
        #print '\n first two chars: ' + first_2_char + '\n'
        if first_2_char == '!q':
            break

        isSendAll = data[:8]
        if isSendAll == '!sendall':
            print 'Sending Message to all Clients!!!\n'
            for c in clientList:
                c.sendall('To all Clients:' + data[8:])
            conn.sendall(data[8:])

        else:
            conn.sendall(reply)
    
    #out of loop
    conn.close()

#Keep talking with client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
    clientList.append(conn)
    #print 'Whatis: ' + conn + '\n'
    #start new thread takes 1st arg as a funciton name to be run
    #second is the tuple of arg to the function
    start_new_thread(clientthread , (conn,))

s.close()
