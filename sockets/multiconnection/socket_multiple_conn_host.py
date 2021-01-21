import socket
import selectors
from types import SimpleNamespace

# this is for the Host/server that will be getting data from clients
# we also add in selectors to handle multiple connections; The main idea of this is to disallow blocking which
# will cause other sockets to stall.


def accept_wrapper(sock: socket.socket):
    # similar to the basic script we get a conn, addr from accepting the socket
    conn, addr = sock.accept()
    print('accepted connection from', addr)
    conn.setblocking(False) # put the socket into non blocking mode
    data = SimpleNamespace(addr=addr, inb=b'', outb=b'') # this will hold the data we want to include along with the socket

    # this might be adding the event read/write that we will get to in the service connection but I am not entirely
    # sure
    events = selectors.EVENT_READ | selectors.EVENT_WRITE # finally we set both read/write events with this
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    # this is really the heart of the multiconnection server
    # in this example we are really either reading in data or writing data to a socket;
    sock = key.fileobj # remember key.fileobj is the actual socket
    data = key.data # this is the associated data

    # this will handle read/write events
    if mask & selectors.EVENT_READ:
        # if the data is ready for reading then this will be found true
        # very similar to the basic version of this script
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data # for this example we are just adding the recv_data to data.outb
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        # if the data is ready for writing then this will be found true
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write; sending data out to the socket
            data.outb = data.outb[sent:]




# set up the selectors
sel = selectors.DefaultSelector()

# This is the IPv4 address for the Wireless LAN adapter called Wi-Fi (on this computer -> MSI 2020)
# if you used 127.0.0.1, then you would be using the localhost and thus a feedback loop (i.e. the network is kinda
# locked into the machine itself). What we did to find the appropirate IPv4 address was to do the following:
#   - first find the name of the card you are using to connect to the local network (wifi)
#   - next run ipconfig command and find the name of the card in the results
#   - get the IPv4 Address; this is what the HOST variable will be for the server (socket_host.py)
#   - lastly get the hostname of the server by running the hostname command; this will be the HOST variable in the
#       client (socket_client.py)
HOST = '192.168.86.29'
PORT = 65000  # port to listen on

print('host info')
print(socket.gethostbyname(HOST))
print(socket.getaddrinfo(HOST, PORT))

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()
print("listening on", (HOST, PORT))

# this sets the socket to no long block; initially you could only have one connectino at a time in the basic script
lsock.setblocking(False)
# this registers the socket and is used with sel.select(); which will wait for events on one or more sockets and then
# read and write data when ready
# data is used to store any arbitrary data you want to store along the socket which is returned when select() returns
sel.register(lsock, selectors.EVENT_READ, data=None)

while True:
    events = sel.select(timeout=None)  # the timeout param will block until there are sockets read for I/O
    # a list is returned when for each socket.key in SelectorKey named tuple that contains a fileobj attribute
    # the key.fileobj is the socket object and the mask is an event mask of operations that are ready
    for key, mask in events:
        # if the key.data is None then we know its from the listening socket and need to run a custom accept() connection

        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)
