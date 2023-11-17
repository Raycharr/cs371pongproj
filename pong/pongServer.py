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

# Server info
PORT = 12321
SERVER_IP = "192.168.1.101"

# Global variables for gamestate and lock
global gamestate 
global gamelock

# Gamestate format:
#       sync, lScore, rScore, lpaddle y, rpaddle y, ball x, ball y, ball x vel, ball y vel
gamestate = [-1, 1, 2, 3, 4, 5, 6, 7, 8]
gamelock = threading.Lock()

# Function that handles threads. Each thread is responsible for
# receiving and sending updates to its respective client.
def client_handler(currClient, playerNum):
    global gamestate
    global gamelock

    if playerNum == 0:
        currClient.send("left".encode())
    else:
        currClient.send("right".encode())

    print("Player {0} started".format(playerNum))
    
    while True:
        
        msg = currClient.recv(2048).decode()
        
        if not msg:
            break
        
        msg = parse_msg(msg)
        print(msg)
        
        #======== BEGIN CRITICAL SECTION ========
        gamelock.acquire()
        
        # check sync of msg and gamestate, use more recent frame
        if gamestate[0] < msg[0]:
            gamestate = msg
        currClient.send(compile_msg(gamestate).encode())
        
        gamelock.release()
        #========= END CRITICAL SECTION =========
        
    #close connection
    currClient.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # Creating the server

server.bind((SERVER_IP, PORT))

server.listen(5)
print("Server listening on port {0}".format(PORT))
print("Server info:{0}".format(server.getsockname()))

clientSocket, clientAddr = server.accept()
print("Client {0} connected".format(clientAddr))

firstClient = threading.Thread(target=client_handler, args = (clientSocket, 0))
print("Player 1 connected, waiting for second player")

clientSocket, clientAddr = server.accept()
print("Client {0} connected".format(clientAddr))

secondClient = threading.Thread(target=client_handler, args = (clientSocket, 1))
print("Player 2 connected, starting game")

firstClient.start()

secondClient.start()