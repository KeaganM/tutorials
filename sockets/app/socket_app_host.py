import socket
import selectors
import traceback

from libserver import Message


# much of the handling of the content logic lies within the message class
sel = selectors.DefaultSelector()
HOST = '192.168.86.29'
PORT = 65000  # port to listen on


def accept_wrapper(sock):
    # nearly identical to the multiconnection version except the message is the Message object from libserver
    conn, addr = sock.accept()  # Should be ready to read
    print("accepted connection from", addr)
    conn.setblocking(False)
    # associated the message object with the socket using sel.register
    # we can get this back when we run the loop down below because we associated it with sel
    message = Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)


# very similar to the multi connect version where we are setting up the server to not allow blocking
host, port = HOST, PORT
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Avoid bind() exception: OSError: [Errno 48] Address already in use
# this is an option added to ensure that the helps avoid the error address already in use error.
# If the server actively closed a connection it will remain in the TIME_WAIT state for about 2 mins
# this is to safeguard against delayed packets in the network being delivered to the wrong address
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
print("listening on", (host, port))
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    # the event loop is designed to catch any errors and keep going if errors are found
    while True:
        # because sel.select is a main driver, and we know that we associated the message with sel in the accept wrapper
        # we can get a reference back to the message
        # it is also responsible for blocking, waiting, and waking up for read and write events
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                message = key.data
                try:
                    # sel.select indirectly is responsible for calling this method
                    message.process_events(mask)
                except Exception:
                    print(
                        "main: error: exception for",
                        f"{message.addr}:\n{traceback.format_exc()}",
                    )
                    message.close()
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
