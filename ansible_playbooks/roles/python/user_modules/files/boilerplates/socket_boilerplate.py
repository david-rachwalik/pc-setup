#!/usr/bin/env python

# Basename: socket_boilerplate
# Description: Common business logic for socket interactions
# Version: 0.6
# VersionDate: 6 Mar 2020

# --- Global Socket Commands ---
# socket_hostname       Returns hostname string
# is_socket             Returns true if connection is a socket instance

# --- SocketContext Class Commands ---
# socket_open           Connect to hostname/port as server or client
# socket_close          Close future requests and shutdown connection
# socket_send_data      Send data to socket
# socket_receive_data   Retrieve data from socket
# socket_next_client    Returns the next client's socket connection and address

from logging_boilerplate import *
import socket

try:
    # Python 2 has both 'str' (bytes) and 'unicode' text
    basestring = basestring
    unicode = unicode
except NameError:
    # Python 3 names the unicode data type 'str'
    basestring = str
    unicode = str

# ------------------------ Methods ------------------------

def is_socket(conn):
    return isinstance(conn, socket._socketobject)


def socket_hostname():
    return socket.gethostname()


def socket_hostport(sock):
    try:
        address = sock.getsockname() # returns tuple(IP, port) for server
        # address = sock.getpeername() # returns tuple(IP, port) for client connection
        return address[1]
    except Exception:
        return 0


# ------------------------ Class Converted Methods ------------------------

def socket_open(hostname, hostport, connect_as="client", timeout=30):
    if not (isinstance(hostname, str) and hostname): raise TypeError("socket_open() expects 'hostname' parameter as string.")
    if not (isinstance(hostname, int) and hostname): raise TypeError("socket_open() expects 'hostname' parameter as integer.")
    connection_whitelist = ["server", "client"]
    if not (connect_as in connection_whitelist): raise TypeError("socket_open() expects 'connect_as' parameter as integer.")
    # Generate socket
    sock_family = socket.AF_INET
    sock_type = socket.SOCK_STREAM
    sock = socket.socket(sock_family, sock_type)
    sock.settimeout(timeout)

    if connect_as == "client":
        # Open socket client to communicate with a server
        try:
            # logger.debug("(SocketContext:socket_open): Connecting to host: {0}:{1}".format(hostname, hostport))
            # Always provide socket.connect() with a tuple
            sock.connect((hostname, hostport))
            # logger.debug("(SocketContext:socket_open): Successfully connected to host: {0}:{1}".format(hostname, hostport))
        except Exception, e:
            # logger.error("An error occurred while connecting socket: {0}".format(e))
            return

    elif connect_as == "server":
        # Open socket server as listener for client requests
        try:
            # logger.debug("(SocketContext:socket_open): Connecting to host: {0}:{1}".format(hostname, hostport))
            # Always provide socket.bind() with a tuple
            sock.bind((hostname, hostport))
            sock.listen(5)
            # logger.debug("(SocketContext:socket_open): Successfully connected to host: {0}:{1}".format(hostname, hostport))
        except Exception, e:
            # logger.error("An error occurred while connecting socket: {0}".format(e))
            return
        
    return sock


def socket_close(sock):
    # logger.debug("(SocketContext:socket_close): Init")
    if not is_socket(sock): raise TypeError("socket_close() expects 'sock' parameter as socket.")
    # logger.debug("(SocketContext:socket_close): Closing connection to host.")

    # Halt all future operations (sending/receiving) on the socket connection
    try:
        sock.shutdown(socket.SHUT_RDWR)
        # logger.debug("(SocketContext:socket_close): Shutdown {0}:{1} socket traffic".format(self.hostname, self.hostport))
    except Exception as exc:
        if exc.errno == 107:
            pass # [Errno 107] Transport endpoint is not connected
        else:
            # logger.error("(SocketContext:socket_close): An error occurred while attempting to close the connection: {0}".format(e))
            return
    # Close the socket connection
    try:
        sock.close()
    except Exception, e:
        # logger.error("(SocketContext:socket_close): An error occurred while attempting to close the connection: {0}".format(e))
        return
    
    # logger.error("(SocketContext:socket_close): Socket connection closed")
    return True


def socket_send_data(sock, message):
    # logger.debug("(SocketContext:socket_send_data): Init")
    if not is_socket(sock): raise TypeError("socket_send_data() expects 'sock' parameter as socket.")
    # logger.debug("(SocketContext:socket_send_data): Sending message: {0}".format(message))
    # Returns None on success; raises Exception on error
    result = sock.sendall(message)
    return result


def socket_receive_data(sock, byteLimit=4096):
    # logger.debug("(SocketContext:socket_receive_data): Init")
    if not is_socket(sock): raise TypeError("socket_receive_data() expects 'sock' parameter as socket.")
    status = ""

    try:
        data = sock.recv(byteLimit)
        # logger.debug("(SocketContext:socket_receive_data): Data received: {0}".format(data))
        if data:
            return (data, None)
        else:
            # A zero length receive indicates socket is closed
            status = "SOCKET_CLOSED"
            # logger.warning("Empty data response indicates socket was closed.")
    except socket.timeout:
        status = "TIMED_OUT"
        # logger.warning("Timed out waiting for data from socket.")
    except socket.error, e:
        status = "SOCKET_ERROR"
        # logger.error("Socket error: {0}".format(e))

    return (None, status)


def socket_next_client(sock):
    # logger.debug("(SocketContext:socket_next_client): Init")
    try:
        (conn, addr) = sock.accept()
        return (conn, addr)
    except socket.timeout:
        # logger.debug("Socket timed out waiting for a client.")
        return (None, None)


# ------------------------ Classes ------------------------

# 'conn' accepts a socket instance, 'server', or 'client'
class SocketContext(object):
    def __init__(self, conn=None, hostname=None, hostport=None, timeout=30):
        # Initial values
        self.family = socket.AF_INET
        self.type = socket.SOCK_STREAM
        # Generate new socket
        if is_socket(conn):
            self.sock = conn
            # TODO: verify connection
        else:
            # Verify values when creating socket connection
            if not (isinstance(hostname, str) and hostname): raise TypeError("SocketContext() expects 'hostname' parameter as string.")
            if not (isinstance(hostport, int) and hostport): raise TypeError("SocketContext() expects 'hostport' parameter as integer.")
            connection_whitelist = ["server", "client"]
            if not (conn in connection_whitelist): raise TypeError("SocketContext() expects 'conn' parameter as choices: {0}".format(connection_whitelist))
            if not isinstance(timeout, int): raise TypeError("SocketContext() expects 'timeout' parameter as interger")

            self.sock = socket.socket(self.family, self.type)
            self.sock.settimeout(timeout)

            if conn == "client":
                # Open socket client to communicate with a server
                try:
                    # logger.debug("(SocketContext:connect): Connecting to host: {0}:{1}".format(hostname, hostport))
                    # Always provide socket.connect() with a tuple
                    self.sock.connect((hostname, hostport))
                    # logger.debug("(SocketContext:connect): Successfully connected to host: {0}:{1}".format(hostname, hostport))
                except Exception, e:
                    # logger.error("An error occurred while connecting socket: {0}".format(e))
                    self.sock = None

            elif conn == "server":
                # Open socket server as listener for client requests
                try:
                    # logger.debug("(SocketContext:ConnectAsServer): Connecting to host: {0}:{1}".format(hostname, hostport))
                    # Always provide socket.bind() with a tuple
                    self.sock.bind((hostname, hostport))
                    self.sock.listen(5)
                    # logger.debug("(SocketContext:ConnectAsServer): Successfully connected to host: {0}:{1}".format(hostname, hostport))
                except Exception, e:
                    # logger.error("An error occurred while connecting socket: {0}".format(e))
                    self.sock = None


    def __repr__(self):
        return self.sock


    def __str__(self):
        return str(self.sock)


    def close(self):
        # logger.debug("(SocketContext:close): Init")
        logger.debug("(SocketContext:close): Closing connection to host.")
        try:
            # Halt send and receive of connection
            self.sock.shutdown(socket.SHUT_RDWR)
            logger.debug("(SocketContext:close): Shutdown {0}:{1} socket traffic.".format(self.hostname, self.hostport))
            # Close all future operations on the socket
            self.sock.close()
            logger.debug("(SocketContext:close): Socket connection closed.")
        except Exception, e:
            logger.debug("(SocketContext:close): An error occurred while attempting to close the connection: {0}".format(e))


    def send_data(self, message):
        # logger.debug("(SocketContext:send_data): Init")
        logger.debug("(SocketContext:send_data): Sending message: {0}".format(message))
        # Returns None on success; raises Exception on error
        result = self.sock.sendall(message)
        return result


    def receive_data(self, byteLimit=4096):
        # logger.debug("(SocketContext:receive_data): Init")
        status = ""
        try:
            data = self.sock.recv(byteLimit)
            logger.debug("(SocketContext:receive_data): Data received: {0}".format(data))
            if data:
                return (data, None)
            else:
                # A zero length receive indicates socket is closed
                status = "SOCKET_CLOSED"
                logger.warning("(SocketContext:receive_data): empty data response indicates socket was closed")
        except socket.timeout:
            status = "TIMED_OUT"
            logger.warning("(SocketContext:receive_data): timed out waiting for data from socket")
        except socket.error, e:
            status = "SOCKET_ERROR"
            logger.error("(SocketContext:receive_data): socket error: {0}".format(e))
        return (None, status)


    # Communicate to the server socket as client
    def ConnectAsClient(self, hostname, hostport):
        logger.debug("(SocketContext:ConnectAsClient): Init")
        if self.connected: return True
        self.hostname = str(hostname)
        self.hostport = int(hostport)
        try:
            logger.debug("(SocketContext:ConnectAsClient): Connecting to host: {0}:{1}".format(self.hostname, self.hostport))
            # Always provide socket.connect() with a tuple
            self.sock.connect((self.hostname, self.hostport))
            self.connected = True
            logger.debug("(SocketContext:ConnectAsClient): Successfully connected to host: {0}:{1}".format(self.hostname, self.hostport))
        except Exception, e:
            logger.error("(SocketContext:ConnectAsClient): An error occurred while connecting socket: {0}".format(e))
        return self.connected


    # Communicate to client sockets as the server
    def ConnectAsServer(self, hostname, hostport):
        logger.debug("(SocketContext:ConnectAsServer): Init")
        if self.connected: return True
        self.hostname = str(hostname)
        self.hostport = int(hostport)
        try:
            logger.debug("(SocketContext:ConnectAsServer): Connecting to host: {0}:{1}".format(self.hostname, self.hostport))
            # Always provide socket.bind() with a tuple
            self.sock.bind((self.hostname, self.hostport))
            self.sock.listen(5)
            self.connected = True
            logger.debug("(SocketContext:ConnectAsServer): Successfully connected to host: {0}:{1}".format(self.hostname, self.hostport))
        except Exception, e:
            logger.error("(SocketContext:ConnectAsServer): An error occurred while connecting socket: {0}".format(e))
        return self.connected


    def NextClient(self):
        logger.debug("(SocketContext:NextClient): Init")
        try:
            (conn, addr) = self.sock.accept()
        except socket.timeout:
            logger.debug("(SocketContext:NextClient): socket timed out waiting for client")
            return (None, None)
        conn = SocketContext(conn)
        return (conn, addr)



# ------------------------ Main program ------------------------

# Initialize the logger
basename = "socket_boilerplate"
log_options = LogOptions(basename)
logger = get_logger(log_options)

if __name__ == "__main__":
    # Returns argparse.Namespace; to pass into function, use **vars(self.args)
    def parse_arguments():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--debug", action="store_true")
        return parser.parse_args()
    args = parse_arguments

    # Configure the logger
    log_level = 20                  # logging.INFO
    if args.debug: log_level = 10   # logging.DEBUG
    logger.setLevel(log_level)
    logger.debug("(__main__): args: {0}".format(args))
    logger.debug("(__main__): ------------------------------------------------")

    # Initialize the socket
    hostname = socket_hostname()
    hostport = 5665
    sock = SocketContext("server", hostname, hostport)
    sock.close()

    # --- Usage Example ---
    # sudo python /root/.local/lib/python2.7/site-packages/socket_boilerplate.py
