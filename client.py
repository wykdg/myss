#!/usr/bin/python
# Filename s5.py
# Python Dynamic Socks5 Proxy
# Usage: python s5.py 1080
# Background Run: nohup python s5.py 1080 &

import socket, sys, select, SocketServer, struct, time
import encrypt

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): pass
server_addr=('127.0.0.1',1100)

class Socks5Server(SocketServer.StreamRequestHandler):

    def handle_tcp(self, sock, remote):
        fdset = [sock, remote]
        self.crypto_sock = encrypt.Encrypt()
        self.crypto_remote= encrypt.Encrypt()
        while True:
            r, w, e = select.select(fdset, [], [])
            if sock in r:
                recv=sock.recv(4096)
                if recv<=0:
                    break
                data = self.crypto_sock.encrypt(recv)

                if len(data) > 0 and remote.send(data) <= 0: break
            if remote in r:
                recv=remote.recv(4096)
                if recv<=0:
                    break
                data = self.crypto_remote.decrypt(recv)
                if len(data) and sock.send(data) <= 0: break

    def handle(self):
        try:
            pass
            sock = self.connection
            # 1. Version
            sock.recv(262)
            sock.send("\x05\x00")
            # 2. Request
            data = self.rfile.read(4)
            mode = ord(data[1])
            addrtype = ord(data[3])
            if addrtype == 1:  # IPv4
                addr = socket.inet_ntoa(self.rfile.read(4))
            elif addrtype == 3:  # Domain name
                addr = self.rfile.read(ord(sock.recv(1)[0]))
            port = struct.unpack('>H', self.rfile.read(2))
            reply = "\x05\x00\x00\x01"
            try:
                if mode == 1:  # 1. Tcp connect
                    remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    # print addr+str(port[0])
                    # remote.connect((addr,port[0]))
                    remote.connect(server_addr)
                    # print (addr,port[0])
                    addr_send=addr+':'+str(port[0])
                    addr_send=encrypt.Encrypt().encrypt(addr_send)
                    remote.send(addr_send)
                    remote.recv(1)
                    pass  # print 'To', addr, port[0] nothing do to.
                else:
                    reply = "\x05\x07\x00\x01"  # Command not supported
                local = remote.getsockname()
                reply += socket.inet_aton(local[0]) + struct.pack(">H", local[1])
            except socket.error:
                # Connection refused
                reply = '\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00'
            sock.send(reply)
            # 3. Transfering
            if reply[1] == '\x00':  # Success
                if mode == 1:  # 1. Tcp connect
                    self.handle_tcp(sock, remote)
        except socket.error:
            pass  # print 'error' nothing to do .
        except IndexError:
            pass


def main():
    filename = sys.argv[0]
    if len(sys.argv) < 2:
        print ('usage: ' + filename + ' port'+ 'remote ip remote port ')
        sys.exit()
    socks_port = int(sys.argv[1])
    server = ThreadingTCPServer(('', socks_port), Socks5Server)
    print  ( 'bind port: %d' % socks_port + ' ok!')
    server.serve_forever()


if __name__ == '__main__':
    main()