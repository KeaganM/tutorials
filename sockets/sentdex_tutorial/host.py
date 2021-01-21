import socket
import time
import pickle

# ****************************************** Basic example *************************************************************
# # again AF_INET is for ipv4 address and SOCK_STREAM is the TCP protocol
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # by using .gethostname() and kept empty we will get the local host (127.0.0.1)
# s.bind((socket.gethostname(), 1234))
# # listen for connections, queue of 5 incase there are a lot of connections
# s.listen(5)
#
# # listen forever
# while True:
#     # accept a connetion if we get one; get an address and another socket object
#     clientsocket, address = s.accept()
#     print(f'Connection from {address} has been established!')
#     # send info to the client socket
#     clientsocket.send(bytes('welcome to the server!', 'utf-8'))
#     # close the client socket
#     clientsocket.close()


# ****************************************** With Header example *******************************************************

# # the idea with headers are to provide you some information about the message
# # similar to headers when making REST requests
#
# # you want a fixed length header that proceeds the message you send; so the program looks for the fixed length
# # header and shouldn't typically be changed up
#
# # can set the header size here
# HEADERSIZE = 10
#
# # again AF_INET is for ipv4 address and SOCK_STREAM is the TCP protocol
# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# # by using .gethostname() and kept empty we will get the local host (127.0.0.1)
# s.bind((socket.gethostname(), 1234))
# # listen for connections, queue of 5 incase there are a lot of connections
# s.listen(5)
#
# # listen forever
# while True:
#     # accept a connetion if we get one; get an address and another socket object
#     clientsocket, address = s.accept()
#     print(f'Connection from {address} has been established!')
#     # send info to the client socket
#
#     msg = 'welcome to the server!'
#     # left align by the variable HEADERSIZE, essentially pushes the left item (len(msg)) by 10
#     # so when the client goes and gets this message, it will want to first extract it out;
#     # it will always know that the len of the msg will be within the first bytes and proceed apporpriately
#     msg = f'{len(msg):<{HEADERSIZE}}' + msg
#
#     # here is an example of how you would keep sending messages from a server to a client
#     while True:
#         time.sleep(3)
#         clientsocket.send(bytes(msg, 'utf-8'))


# ****************************************** With Pickle example *******************************************************

HEADERSIZE = 10

# again AF_INET is for ipv4 address and SOCK_STREAM is the TCP protocol
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# by using .gethostname() and kept empty we will get the local host (127.0.0.1)
s.bind((socket.gethostname(), 1234))
# listen for connections, queue of 5 incase there are a lot of connections
s.listen(5)

# listen forever
while True:
    clientsocket, address = s.accept()
    print(f'Connection from {address} has been established!')

    d = {1: 'hey', 2: 'there'}
    # turns it into bytes
    msg = pickle.dumps(d)
    # only have to change the first part of the msg into bytes and then add the content like so
    msg = bytes(f'{len(msg):<{HEADERSIZE}}','utf-8') + msg

    clientsocket.send(msg)

