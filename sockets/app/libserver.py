import sys
import selectors
import json
import io
import struct


'''
note the handling of sockets and the information between them like this is very similar to web requests/responses
where we have headers, payloads/content, etc.

in this case we have the following headers passed along:
    - fixed-length header: byte order of the machine which uses sys.byteorder; may not be required
        - this is important to consider if you receive bytes in a format that is not native to your machines CPU
        - you may need to convert it to the native byte order used by your machine (Endianness)
    - json headers: subheaders that inform the reciever about the content of the payload and may include things like
        content-length (specified in the fixed-length header), content-type, content-encoding, etc...
    - payload/content: the actual content, processing at this point would only come after the above information was 
        processed. Aside from the content, type, encoding, and length are specified as well but all would have already
        been defined by the json headers. 
'''

request_search = {
    "morpheus": "Follow the white rabbit. \U0001f430",
    "ring": "In the caves beneath the Misty Mountains. \U0001f48d",
    "\U0001f436": "\U0001f43e Playing ball! \U0001f3d0",
}


class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _create_response_json_content(self):
        # just a method to create a json content response
        action = self.request.get("action")
        if action == "search":
            query = self.request.get("value")
            answer = request_search.get(query) or f'No match for "{query}".'
            content = {"result": answer}
        else:
            content = {"result": f'Error: invalid action "{action}".'}
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response

    def _create_response_binary_content(self):
        response = {
            "content_bytes": b"First 10 bytes of request: "
            + self.request[:10],
            "content_type": "binary/custom-server-binary-type",
            "content_encoding": "binary",
        }
        return response

    def process_events(self, mask):
        # this is essentially the part in the multi connect version that preforms the checks if the socket is ready for
        # read/write
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        # the read method is called and calls the socket.recv() to read and store the data from the socket
        # The _read method above does the actual work of calling socket.recv() which we say in past iterations
        # This method contains state checks to ensure ensure each part of the message arrives as expected
        # it does this by making sure there are enough bytes that have been read into the buffer; this is all due to
        # the fact that we may not get the full message and socket.recv() may need to be called again
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        # first check for a request and if one does not exist then create create_respponse is called
        if self.request:
            if not self.response_created:
                self.create_response()
        # this is where you would see the socket.send() in past versions
        self._write()

    def close(self):
        print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                "error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_protoheader(self):
        # so this one would check and process the fixed length header
        # when the server has read at least 2 bytes the fixed length header can be processed
        # remember the fixed length header is a 2-byte integer that contains the length of the json header
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            # the processing involves getting the length of the json header
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            # after processing, remove this from the buffer
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        # this one would check and process for the json header
        # again, like the fixed length header, if there are enough bytes to process then this is run
        hdrlen = self._jsonheader_len
        # check to see if there are enough bytes
        if len(self._recv_buffer) >= hdrlen:
            # _json_decode() is run to deserialize the json header into a dictionary
            # de/serialization is the process by which an object is converted into a byte stream (serial) or
            # reconstructure from a byte stream (deserial)
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            # remove the jsonheader from the buffer
            self._recv_buffer = self._recv_buffer[hdrlen:]
            # checks for certain headers ni the jsonheader
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_request(self):
        # lastly this would check and process the content
        # this is the actual payload/content
        # similar to the fixed length header and json header, we check to see if there is enough bytes
        # if so we move on and grab the data
        # how do we know if there are enough bytes? we check the content-length in the json header
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        # get the data here
        data = self._recv_buffer[:content_len]
        # remove it from the buffer
        self._recv_buffer = self._recv_buffer[content_len:]
        # check to see if the content type is text/json
        # may be able to add in other types of content-types to handle data differnelty
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            print("received request", repr(self.request), "from", self.addr)
        else:
            # Binary or unknown content-type
            self.request = data
            print(
                f'received {self.jsonheader["content-type"]} request from',
                self.addr,
            )
        # Set selector to listen for write events, we're done reading.
        # note interested in reading at this point so we set the event mask to 'w' (write)
        self._set_selector_events_mask("w")

    def create_response(self):
        # once we are done reading and the _set_selector_events_mask has been set with 'w' we can create a response
        # in this case if we have a content-type of text/json we will create a json response
        if self.jsonheader["content-type"] == "text/json":
            # you can sed it up to handle other content-types by just adding the logic to check and a method to create
            response = self._create_response_json_content()
        else:
            # Binary or unknown content-type
            response = self._create_response_binary_content()
        message = self._create_message(**response)
        # set response_created and add the message to the send buffer
        self.response_created = True
        self._send_buffer += message