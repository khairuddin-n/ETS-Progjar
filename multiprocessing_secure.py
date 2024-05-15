import os
from socket import *
import socket
import time
import sys
import multiprocessing
import ssl
from http import HttpServer

httpserver = HttpServer()

class ProcessTheClient(multiprocessing.Process):
    def __init__(self, connection, address, context):
        self.connection = connection
        self.address = address
        self.context = context
        multiprocessing.Process.__init__(self)

    def run(self):
        rcv = ""
        try:
            self.secure_connection = self.context.wrap_socket(self.connection, server_side=True)
            while True:
                data = self.secure_connection.recv(32)
                if data:
                    d = data.decode()
                    rcv = rcv + d
                    if rcv[-2:] == '\r\n':
                        hasil = httpserver.proses(rcv)
                        hasil = hasil + "\r\n\r\n".encode()
                        self.secure_connection.sendall(hasil)
                        rcv = ""
                        self.secure_connection.close()
                else:
                    break
        except OSError as e:
            pass
        self.connection.close()

class Server(multiprocessing.Process):
    def __init__(self, hostname='testing.net'):
        self.the_clients = []
        self.hostname = hostname
        cert_location = os.getcwd() + '/certs/'
        self.context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.context.load_cert_chain(certfile=cert_location + 'domain.crt',
                                     keyfile=cert_location + 'domain.key')
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        multiprocessing.Process.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', 8004))
        self.my_socket.listen(1)
        while True:
            self.connection, self.client_address = self.my_socket.accept()
            clt = ProcessTheClient(self.connection, self.client_address, self.context)
            clt.start()
            self.the_clients.append(clt)

def main():
    svr = Server()
    svr.start()

if __name__ == "__main__":
    main()
