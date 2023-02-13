#!/usr/bin/env python3

# Install Packages
import pip

packages = ['python-osc']

def install(package):
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        pip._internal.main(['install',package])

print("Installing Necessary Packages\n")

for package in packages:
    install(package)

import socket
import sys
from pythonosc import udp_client
import configparser
import os

serv_ip     = "127.0.0.1"
serv_port   = 9002
server      = (serv_ip, serv_port)
host_ip     = "0.0.0.0"
host_port   = 0

def main():
    
    try:
        print("\nHandshaking With Server")
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

    peer_data, peer_addr    = sockfd.recvfrom(128)
    peer_data               = peer_data.decode()
    peer_ip, peer_port      = peer_data.split(":")
    peer_port               = int(peer_port)

    print("Received Peer")
    print("IP: {}".format(peer_ip))
    print("PORT: {}".format(peer_port))

    print("\nCommencing Holepunch")

    print("Connecting To: {}:{}".format(peer_ip,peer_port))
    print("{} Bytes Sent".format(sockfd.sendto(b'0', (peer_ip,peer_port))))

    # Parse Config File
    config = configparser.ConfigParser(allow_no_value=True)
    config.optionxform = str
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config_path = os.path.join(__location__, 'parameter_list.cfg')
    assert os.path.exists(config_path)
    config.read(config_path)

    # Initialise OSC Client
    client = udp_client.SimpleUDPClient("127.0.0.1",9000)

    while(True):
        message, addr = sockfd.recvfrom(128)

        if (message == b'\0'):
            continue
        
        if( not (addr[0] == peer_ip)):
            continue

        message = message.decode()
        message = message.split(' ')
        address = message[0]
        value   = message[1]

        if("/avatar/parameters/" in address):
            parameter   = address[19:]
            if( config.has_option("PARAMETERS",parameter) ):
                print("{} {}".format(address,value))
                client.send_message(address, float(value))
    return

if __name__ == '__main__':
    main()
