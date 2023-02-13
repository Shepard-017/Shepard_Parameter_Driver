#!/usr/bin/env python3

# Install Packages
import pip

packages = ['python-osc']

def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install',package])

for package in packages:
    install(package)

# Import Packages and Libraries
import socket
import sys
import threading
from time import sleep
from pythonosc import dispatcher
from pythonosc import osc_server

serv_ip     = "contrivingshepard.ddns.net"
# serv_ip = '127.0.0.1'
serv_port   = 9002
server      = (serv_ip, serv_port)
host_ip     = "0.0.0.0"
host_port   = 0
dispatcher  = dispatcher.Dispatcher()

# Maintain UDP P2P Connection
def maintain_conn(peer_ip: str, peer_port: int, sockfd):
    while(True):
        sockfd.sendto(b'\0',(peer_ip,peer_port))
        sleep(20)
    return

# Listen to OSC from VRC
def osc_listener(address: str, args: list, val: float) -> None:
    message = "{} {}".format(address, val)
    print(message)
    args[2].sendto(message.encode(), (str(args[0]), int(args[1])))
    return

# Send OSC information to recipient
def send_osc(peer_ip: str, peer_port: int, sockfd):
    osc_port    = 9001
    local_ip    = '127.0.0.1'

    vrc_listener = osc_server.BlockingOSCUDPServer((local_ip, osc_port), dispatcher)
    dispatcher.map("*",osc_listener,peer_ip,peer_port,sockfd)

    while(True):
        vrc_listener.handle_request()
    return

def main():
    # Attempt to create a socket and establish a connection with the server
    try:
        print("Handshaking With Server")
        sockfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sockfd.bind((host_ip,host_port))
        sockfd.sendto(b'0', server)
        while(True):
            data = sockfd.recv(128).decode()
            if(data.strip() == 'Ready'):
                print("Checked In With Server: Waiting")
                break
    except:
        print("Failed To Establish Socket")
        sys.exit()

    # Receive and parse peer address
    peer_data, peer_addr    = sockfd.recvfrom(128)
    peer_data               = peer_data.decode()
    peer_ip, peer_port      = peer_data.split(":")
    peer_port               = int(peer_port)

    # IP Overwrite For Local Server Hosting On Receiver Endpoint
    if(peer_ip == '127.0.0.1'):
        peer_ip = serv_ip

    print("Received Peer")
    print("IP: {}".format(peer_ip))
    print("PORT: {}".format(peer_port))

    print("\nCommencing Holepunch")

    print("Connecting To: {}:{}".format(peer_ip,peer_port))
    print("{} Bytes Sent".format(sockfd.sendto(b'Ready', (peer_ip,peer_port))))

    # Spawn 2 threads:
    #   One to maintain the connection
    #   One to translate OSC info

    t1 = threading.Thread(target = maintain_conn,   args = (peer_ip, peer_port, sockfd))
    t2 = threading.Thread(target = send_osc,        args = (peer_ip, peer_port, sockfd))
    t1.start()
    t2.start()
    return

if ( __name__ == '__main__' ):
    main()
