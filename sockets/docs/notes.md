# Ultra basic example of a socket

```python
# host #######################################################

import socket

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((socket.gethostname(),65000))

s.listen(5)

while True:
    client_socket,address = s.accept()

    msg = client_socket.recv(1024)
    print(msg)

# client #######################################################

import socket

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# s.bind((socket.gethostname(),65000))

s.connect((socket.gethostname(),65000))
msg = b'hello'

s.sendall(msg)
```

simple example fo a client connecting to a server and sending a message to the server. 