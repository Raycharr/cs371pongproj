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

SCRN_WD = 250
SCRN_HT = 250
PORT = 12345
SERVER_IP = "localhost"


# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

def client_handler(currClient, playerNum):
    playerZero = (SCRN_WD, SCRN_HT, "left")
    playerOne = (SCRN_WD, SCRN_HT, "right")
    #main loop for handling connected clients
    if playerNum == 0:
        currClient.send(playerZero.encode())
    else:
        currClient.send(playerOne.encode())

    while True:
        msg = currClient.recv(1024).decode()
        if msg == 'something weird':
            break
        #recieve packet from client
        #check sync
        #do other things
    #close connection
    currClient.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # Creating the server

server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Working on localhost need this

server.bind((SERVER_IP, PORT))

server.listen(5)
print("Server listening on port {0}".format(PORT))

clientSocket, clientAddr = server.accept()
print("Client {0} connected".format(clientAddr))

firstClient = threading.Thread(target=client_handler, args = (clientSocket, 0))
print("Player 1 connected, waiting for second player")

clientSocket, clientAddr = server.accept()
print("Client{0} connected".format(clientAddr))

secondClient = threading.Thread(target=client_handler, args = (clientSocket, 1))
print("Player 2 connected, starting game")

firstClient.start()

secondClient.start()