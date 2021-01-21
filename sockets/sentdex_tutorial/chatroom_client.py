import socket
import select
import errno
import sys

# errno is used to match specific error codes; try to receive messages until we can't and handle that specific error
# due to not receiving a message

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234

my_username = input('username: ')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))
client_socket.setblocking(False)  # receive functionality won't be blocking

# the first thing we want to send is the username info *****************************************************************

username = my_username.encode('utf-8')
# again this pushes the left item by the length of the right item; so if we have a len of 4 for our username we will get
#   '4          ' as the header and again we know the length is fixed and thus know how to handle it appropriately
username_header = f'{len(username):<{HEADER_LENGTH}}'.encode('utf-8')

client_socket.send(username_header + username)

# next we want to iterate forever and send/receive messages ************************************************************

# this kinda acts like the main part of the app, where we want everyting to keep running
while True:
    # so we have to essentially either press enter or a new message to get new messages because
    # input is blocking; if you were to remove this somehow and accept user input it would be fluid
    # and you wouldn't have to press enter/send a message
    message = input(f'{my_username} > ')

    # if there is a new message (i.e. message above is not empty)
    if message:
        message = message.encode('utf-8')
        message_header = f'{len(message):<{HEADER_LENGTH}}'.encode('utf-8')
        client_socket.send(message_header + message)

    try:
        while True:
            # receive things

            # based on how the server is sending messages back out to clients the stream looks like:
            # username[header] + username[data] + message[header] + message[data]

            # first lets get the username ******************************************************************************
            username_header = client_socket.recv(HEADER_LENGTH)
            # if we did not get any data
            if not len(username_header):
                print('connection closed by the server')
                sys.exit()
            username_length = int(username_header.decode('utf-8').strip())  # are expecting: '*          '
            username = client_socket.recv(username_length).decode('utf-8')
            # once we have gotten to this point, we should be at the point of the message header
            # so we are given data stream (above) and we essentially parse through the uersname bits
            # now all that is left is the message bits

            # next lets get the message ********************************************************************************
            message_length = int(client_socket.recv(HEADER_LENGTH).strip())
            message = client_socket.recv(message_length).decode('utf-8')

            print(f'{username} > {message}')

    except IOError as e:
        # these are some errors we might see depending on the os if there are no more messages
        # but we are expecting some of these so we want to handle these appropriately
        # really we don't care for these errors so keep this program running
        # if both errors are present then just skip
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('reading error', str(e))
            sys.exit()
        continue

    except Exception as e:
        print('General error', str(e))
        sys.exit()
