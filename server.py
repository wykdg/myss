#!/usr/bin/python
# Filename s5.py
# Python Dynamic Socks5 Proxy
# Usage: python s5.py 1080
# Background Run: nohup python s5.py 1080 &

import socket, sys, select, SocketServer, struct, time


class ThreadingTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer): pass

class Socks5Server(SocketServer.StreamRequestHandler):
    def handle_tcp(self, sock, remote):
        fdset = [sock, remote]
        while True:
            r, w, e = select.select(fdset, [], [])
            if sock in r:
                if remote.send(sock.recv(4096)) <= 0: break
            if remote in r:
                if sock.send(remote.recv(4096)) <= 0: break

    def handle(self):
        try:
            pass
            sock = self.connection

            remote_addr=sock.recv(262)
            sock.send("\x00")

            addr,port=remote_addr.split(':')
            port=int(port)

            remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote.connect((addr,port))

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