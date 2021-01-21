import socket
import pickle

# ****************************************** Basic example *************************************************************

# s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#
# # again we are connecting to the localhost and we can get that using gethostname()
# # we will probabably use an actual ip address
# s.connect((socket.gethostname(),1234))
#
# # # we can recv data with how big the chunk of data will be, in this case 1024 bytes
# # # larger files may require a larger number
# # # now in this example, the server is wanting to send the message: 'welcome to the server!'
# # # if you were to set the s.recv to 8 (s.recv(8)) you would only get 'welcome '(with the space at the end)
# # # this is essentially a stream/buffer
# # msg = s.recv(1024)
#
# # # you can also do b'my message'
# # # in this case we are sending a byte stream and decoding it and it was set to utf-8
# # print(msg.decode('utf-8'))
#
# # now in the case where you buffer is to small, what you can do is put it in a while loop which will
# # iterate for as long as it needs to get recv the entire message like below
# while True:
#     # sending 8 bytes at a time
#     msg = s.recv(1024)
#     print(msg.decode('utf-8'))
#     # should get:
#     #
#     # welcome
#     # to the s
#     # erver!
#
#
#     # you will need a break statement to get out of this loop, which  you can do the following:
#     if len(msg) >= 0:
#         # s.close()
#         break

# ****************************************** With Header example *******************************************************
# HEADERSIZE = 10
# s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#
# s.connect((socket.gethostname(),1234))
#
# # in this case we are reading in the fixed header length
# while True:
#     full_msg = ''
#     new_msg = True
#     # this should keep the socket open
#     while True:
#         # how much to recv (16 bytes)
#         msg = s.recv(16)
#         # if we have a new message, lets get msglen by grabbing everything from the beginning of what was sent
#         # to the index of HEADERSIZE; in this case we would end up sending 'len(msg)          ' which we convert
#         # to an int here; this may not work in other languages but we would maybe just have to strip it
#         # really what we are doing here is getting a fixed length header, which essentially extends out by
#         # 10 characters maxed; if we ended up needing more, say we have a larger message number, then we may need
#         # to include a larger fixed length header; this is simalar to the other tutorial where we used a
#         # key/value pairs to dicated the headers (similar to REST headers)
#         if new_msg:
#             print(f' new message length: {msg[:HEADERSIZE]}')
#             msglen = int(msg[:HEADERSIZE])
#             new_msg = False
#         # add whatever we get to the full_msg; if the len of full_msg - HEADERSIZE (so everything after the headersize)
#         # and is eqal to msglen which we know from getting that above, we can
#         full_msg += msg.decode('utf-8')
#         if len(full_msg) - HEADERSIZE == msglen:
#             print('full msg recvd')
#             print(full_msg[HEADERSIZE:])
#             new_msg = True
#             full_msg = ''

# ****************************************** With Pickle example *******************************************************


HEADERSIZE = 10
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

s.connect((socket.gethostname(),1234))

# in this case we are reading in the fixed header length
while True:
    full_msg = b''
    new_msg = True
    while True:
        msg = s.recv(16)

        if new_msg:
            print(f' new message length: {msg[:HEADERSIZE]}')
            msglen = int(msg[:HEADERSIZE])
            new_msg = False

        full_msg += msg
        if len(full_msg) - HEADERSIZE == msglen:

            print('full msg recvd')
            print(full_msg[HEADERSIZE:])
            # simply have to load a pickle with pickle.loads
            d = pickle.loads(full_msg[HEADERSIZE:])
            print(d)


            new_msg = True
            full_msg = ''