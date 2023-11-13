# =================================================================================================
# Contributing Authors:	    Alexander Wyatt & Caroline Waters
# Email Addresses:          ajwy223@uky.edu, cewa241@uky.edu
# Date:                     11/6/2023
# Purpose:                  Implements the server on which the clients will connect.
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading
from assets.code.helperCode import parse_msg, compile_msg

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games


def client_handler(currClient, playerNum):
    #main loop for handling connected clients
    while True:
        msg = currClient.recv(1024)
        if msg == 'something weird':
            break
        #recieve packet from client
        #check sync
        #do other things
    #close connection
    currClient.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # Creating the server

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Working on localhost need this

server.bind(("localhost", 12345))

server.listen(5)

clientSocket, clientAddr = server.accept()

firstClient = threading.Thread(target=client_handler, args = (clientSocket, 0))

clientSocket, clientAddr = server.accept()

secondClient = threading.Thread(target=client_handler, args = (clientSocket, 1))