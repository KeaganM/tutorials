import socket
import json


# note this was a script designed to run on a separate machine like a raspberry py
HOST = 'MSI'
PORT = 65000

# host name
# can pass in the ip address of the host to get the name (or use hostname on the host machine)
print(socket.gethostbyname(HOST))

# address info
# info regarding the address
print(socket.getaddrinfo(HOST,PORT))

test = {
    'data': [1,2,3]
}

# we want to pass in a byte string eventually so use json.dumps
test_json = json.dumps(test)

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.connect((HOST,PORT))
    # need to encode the data as a byte string
    s.sendall(str.encode(test_json))
    data = s.recv(1024)

print('received',repr(data))