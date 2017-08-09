#!/usr/bin/python
# Filename s5.py
# Python Dynamic Socks5 Proxy
# Usage: python s5.py 1080
# Background Run: nohup python s5.py 1080 &

import socket, sys, select, SocketServer, struct, time
import encrypt

class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): pass

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
                data = self.crypto_sock.decrypt(recv)

                if len(data) > 0 and remote.send(data) <= 0: break
            if remote in r:
                recv=remote.recv(4096)
                if recv<=0:
                    break
                data = self.crypto_remote.encrypt(recv)
                if len(data) and sock.send(data) <= 0: break

    def handle(self):
        try:
            pass
            sock = self.connection
            remote_addr=sock.recv(262)
            remote_addr=encrypt.Encrypt().decrypt(remote_addr)
            sock.send("\x00")


            remote_ip,port=remote_addr.split(':')
            port=int(port)

            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.connect((remote_ip,port))

            self.handle_tcp(sock, remote)
        except socket.error:
            pass  # print 'error' nothing to do .
        except IndexError:
            pass


def main():
    filename = sys.argv[0]
    if len(sys.argv) < 2:
        print ('usage: ' + filename + ' port')
        sys.exit()
    socks_port = int(sys.argv[1])
    server = ThreadingTCPServer(('', socks_port), Socks5Server)
    print  ( 'bind port: %d' % socks_port + ' ok!')
    server.serve_forever()


if __name__ == '__main__':
    main()