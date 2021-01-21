import socket
import selectors
from types import SimpleNamespace

# this is the multiple connection client file used when we want to connect multiple clients to a server that is
# designed for multiple connections; similar to the host version but we are listening for connections
sel = selectors.DefaultSelector()

HOST = '192.168.86.29'
PORT = 65000



messages = [b"Message 1 from client.", b"Message 2 from client."]

# this will start to listen for connections
def start_connections(host, port, num_conns):
    # this is essentially the equalivent to the top of the host version
    server_addr = (host, port)
    for i in range(0, num_conns):
        connid = i + 1
        print("starting connection", connid, "to", server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # just like the host version we set up the socket like usual
        sock.setblocking(False) # set blocking to false

        # this is used instead of connect() due to connect() will raise an error
        # this will just return an error indicator instead of raising an error while we are trying to connect
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE # same as the host version
        data = SimpleNamespace(
            connid=connid,
            msg_total=sum(len(m) for m in messages),
            recv_total=0,
            messages=list(messages),
            outb=b"",
        ) # this is all the data we want to have attached to our socket which we dump into the SimpleNamespace
        sel.register(sock, events, data=data) # register the socket just like in the host version


def service_connection(key, mask):
    # fundamentally the same as the host version but tracks the number of bytes that are received by the server
    # This is done so that the connection is closed when the data is sent; the server depends on this otherwise
    # the connection would remain open; this may be something to consider guarding against on the server side.
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            print("received", repr(recv_data), "from connection", data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total: # the check to see if the number of bytes the server received
            print("closing connection", data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("sending", repr(data.outb), "to connection", data.connid)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]


host, port, num_conns = HOST,PORT,1
start_connections(host, int(port), int(num_conns))

try:
    while True:
        events = sel.select(timeout=1)
        if events:
            for key, mask in events:
                service_connection(key, mask)
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()