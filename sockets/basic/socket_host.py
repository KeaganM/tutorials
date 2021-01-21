import socket


# this is for the Host/server that will be getting data from clients

# This is the IPv4 address for the Wireless LAN adapter called Wi-Fi (on this computer -> MSI 2020)
# if you used 127.0.0.1, then you would be using the localhost and thus a feedback loop (i.e. the network is kinda
# locked into the machine itself). What we did to find the appropirate IPv4 address was to do the following:
#   - first find the name of the card you are using to connect to the local network (wifi)
#   - next run ipconfig command and find the name of the card in the results
#   - get the IPv4 Address; this is what the HOST variable will be for the server (socket_host.py)
#   - lastly get the hostname of the server by running the hostname command; this will be the HOST variable in the
#       client (socket_client.py)
HOST = '127.0.0.1'
PORT = 65000  # port to listen on

print('host info')
print(socket.gethostbyname(HOST))
print(socket.getaddrinfo(HOST,PORT))



# uses a context manager (with)
# the args passed to socket.socket are the address family and socket type
# so AF_INET is IPV4 address family (AF) and the SOCK_STREAM is the TCP protocol
# TCP (Transmission control protocol) is a good default protocol to use since packets of data dropped in the network
#   are detected and retransmitted by the sender and has in-order data delivery

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # AF_INET is expecting a host and port; note the IPv4 formatting for host should be used
    # should be a tuple of the HOST and PORT
    s.bind((HOST,PORT))

    # this will enable the server to listen for connections; note you can set the number of connections
    # using the backlog parameter
    s.listen()

    conn, addr = s.accept() # this will enable the server to accept connections; returns a new connection object

    # this is used to handle the connection; an infinte loop is created and reads the data whenever it is sent
    # by the client; if conn.recv gets an empty byte object (b'') then the client closed the connection and the
    # loop is terminated. The connection is then closed with the with statement (another context manager situation).
    with conn:
        print('Connected by', addr)
        while True:
            # the bufsize arg is set to 1024 which means the max amount of data to be received is 1024 bytes
            # notte
            data = conn.recv(1024)
            print('data received',repr(data))
            if not data:
                break

            # to avoid having to make sure we check that all the data was sent we do sendall
            conn.sendall(data)
