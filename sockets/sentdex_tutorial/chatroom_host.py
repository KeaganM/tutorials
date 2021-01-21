import socket
import select

'''
The goal of this program (and the client version) is to create a chatroom where multiple clients can connect to a 
single server and send messages back and forth using the server as a nexus. We do this by doing the following
here in this script:

    1. set up the server like you would normally
        - set header length, ip, port, 
        - bind the socket, listent
    2. next we want to set up a sockets list and a clients dict
        - this will be used to see who is connected (sockets list) and some basic info about each connection
            (client dict)
    3.  - the receive message function will first receive the header of a client socket.
        - if there is no header then we return false and something happened to the connection
        - otherwise we will handle the header and return the header/data
    4. next the main portion of the program starts in a while loop
    5. we will first use select and only worry about reading sockets and exceptions
    6. iterate over read sockets and check to see if one is the server (one should be by default)
    7. if the socket in the current iteration is the server then we can use it to accpt a client
        - next we want two things, the username info and the message info that will be sent by the client
        - if the user name is false we break otherwise we add the client to socket list
            - this will allow us to iterate over it and since we handle client sockets different than server sockets
                we will send messages out to them
        - add username info to the clients dict (keep track of who is who)
        - next we try to get the message; note we should be able to receive the message next since we the headers
            we use indicate how long the username/message should be, so our cursor should end up starting at the 
            message header
        - check if the message is false and if so remove the socket from the list
    8. lastly we want to send messages we get to all the other clients
        - iterate over all clients in the clients list
        - if the client is currently not the same as the current socket we are no then we will send a message
            with both the username info and the message info 
'''


# select gives use operating system level I/O capabilities

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234

# AF stands for address family and INET just means the internet
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# one options to handle ports that are in use
# allow use to reconnect to the socket above
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

# as clients connect, the clients will append to the list
sockets_list = [server_socket]

clients = dict()


def receive_message(client_socket):
    try:
        # remember, recv(<number>) is the amount of bytes we will get
        # by doing this we are only going to recieve the header length
        message_header = client_socket.recv(HEADER_LENGTH)

        # if we did not get any data, the connection was closed
        if not len(message_header):
            return False
        # with how we are going to do the header we can add a strip to get the content length
        # note if we do this differently like with CORS Headers, we would have to handle it more
        # appropriately since it would come in as a json
        # header will look like: '10      '
        message_length = int(message_header.decode('utf-8').strip())
        # remember, we pass in a header to determine what the message length will be, we know the header
        # is a fixed length so we can go head and hard code in a 10 (with HEADER_LENGTH) since we decided that is what
        # we want to use. With that, our messages can now be variable length, since what is happening on the client side
        # is a header is being create with the len of the message (again in the header and set to a fixed length of
        # HEADER_LENGTH) and thus we can extract the message len and use that in a new recv statement to get the rest
        # of the message; other headers can be used to provide more information on what kind of data we are dealing with
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    # hit this is the client closed aggressively
    except:
        return False

print("server started!")
while True:
    # takes in 3 params, sockets to read, sockets to write , and sockets we might error on
    # we are focused on the read sockets
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    for notified_socket in read_sockets:
        # this is for when someone connects, here we are just getting user info ****************************************
        # if someone connects
        # for this the client will send to major things, some user info, and any messages that are typed up for the
        # chatroom
        if notified_socket == server_socket:
            client_socket, client_address = server_socket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue
            sockets_list.append(client_socket)
            # we use client_socket as the key in the clients dict
            clients[client_socket] = user

            print(
                f'Accept new conection from {client_address[0]}:{client_address[1]} username:{user["data"].decode("utf-8")}')
        else:
            message = receive_message(notified_socket)
            if message is False:
                print(f"Closed connection from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # for sending data to the other clients
            for client_socket in clients:
                # don't want to send the message right back to the client that posted it
                if client_socket != notified_socket:
                    # sending in the username data and the message data; remember everythign needs a header
                    # and content, and user/message are two separate things
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
