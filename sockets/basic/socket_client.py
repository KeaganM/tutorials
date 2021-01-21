import socket


# this is for the client; much simpler as it is just sending a quick hello world and waiting for a response
# this one is just a test and designed to be used in a feedback loop with the socket_host.py; that file needs to have
# the host set to 27.0.0.1 in order for them to talk to each other.

HOST = '127.0.0.1'  # local host
PORT = 65000  # port to listen on

# similar to the host script
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT)) # connect to the host with HOST and PORT
    s.sendall(b'Hello, world') # send the data
    data = s.recv(1024) # receive a response from the server

print('Received', repr(data))
