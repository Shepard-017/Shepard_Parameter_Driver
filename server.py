#!/usr/bin/env python3

import socket
import sys

serv_ip = "0.0.0.0"
serv_port = 9002

def handshake():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((serv_ip, serv_port))
    clients = []

    while(True):
        print("Awaiting Connections")
        data, addr = sock.recvfrom(128)
        clients.append(addr)
        print("Connection From: {}".format(addr))
        sock.sendto(b'Ready', addr)

        if(len(clients) == 2):
            c1 = clients.pop()
            c1_addr, c1_port = c1
            c2 = clients.pop()
            c2_addr, c2_port = c2

            print("Exchanging Client Info\n")
            sock.sendto('{}:{}'.format(c1_addr, c1_port).encode(), c2)
            sock.sendto('{}:{}'.format(c2_addr, c2_port).encode(), c1)

            break

    return

def main():
    while(True):
        handshake()
    return

if __name__ == '__main__':
    main()