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

SCRN_WD = 640
SCRN_HT = 480
PORT = 12321
SERVER_IP = "192.168.1.101"

#sync, lScore, rScore, lpaddle y, rpaddle y, ball x, ball y, ball x vel, ball y vel
global gamestate 
global gamelock
gamelock = threading.Lock()
gamestate = [-1, 1, 2, 3, 4, 5, 6, 7, 8]


# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games

def swap_lr(statelist):
    statelist.insert(5, statelist[3])
    statelist.pop(3)
    return statelist

print(gamestate)
gamestate = swap_lr(gamestate)
print(gamestate)


def client_handler(currClient, playerNum):
    global gamestate
    #global gamelock
    #playerZero = (SCRN_WD, SCRN_HT, "left")
    #playerOne = (SCRN_WD, SCRN_HT, "right")
    #main loop for handling connected clients
    if playerNum == 0:
        currClient.sendall("left".encode())
    else:
        currClient.sendall("right".encode())

    print("Player {0} started".format(playerNum))
    
    while True:
        
        msg = currClient.recv(2048).decode()
        
        if not msg:
            break
        
        
        msg = parse_msg(msg)
        #if playerNum == 1:
        #    print("player {0} is swapping".format(playerNum))
        #    swap_lr(msg)
        #print("player {0} received {1}".format(playerNum, msg))
        
        gamelock.acquire()
        
        if gamestate[0] < msg[0]:
            gamestate = msg

        currClient.sendall(compile_msg(gamestate).encode())
        #print("player {0} sent gamestate".format(playerNum))
        gamelock.release()
        
    #close connection
    currClient.close()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      # Creating the server

#server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)    # Working on localhost need this

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