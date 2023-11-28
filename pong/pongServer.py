# =================================================================================================
# Contributing Authors:	    Alexander Wyatt & Caroline Waters
# Email Addresses:          ajwy223@uky.edu, cewa241@uky.edu
# Date:                     11/6/2023
# Purpose:                  Implements the server on which two clients will connect, controls the
#                           synchronization of the client data.
# Misc:                     <>
# =================================================================================================

import socket
import threading
from assets.code.helperCode import parse_msg, compile_msg, PAYLOAD_SIZE

# Server info
PORT = 12321
SERVER_IP = "100.70.246.124"

# Global variables for gamestate and lock
global gamestate
global gamelock

# Gamestate format:
#sync, lScore, rScore, lpaddle y, rpaddle y, lpaddle moving, rpaddle moving, ball x, ball y, ball vx, ball vy
#0   , 1     , 2     , 3        , 4        , 5             , 6             , 7     , 8     , 9      , 10
gamestate = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
gamelock = threading.Lock()

# Function that handles threads. Each thread is responsible for
# receiving and sending updates to its respective client.
def client_handler(currClient:socket.socket, playerNum:int) -> None:
    
    # Import global variables into scope of function
    global gamestate
    global gamelock

    # First player to connect is left side, second player is right side
    if playerNum == 0:
        currClient.send("left".encode())
    else:
        currClient.send("right".encode())

    print(f"Player {playerNum} started")
    
    while True:
        
        msg = currClient.recv(PAYLOAD_SIZE).decode()
        
        if not msg:
            break
        
        msg = parse_msg(msg)
        print(msg)
        
        #======== BEGIN CRITICAL SECTION ========
        gamelock.acquire()
        
        # check sync of msg and gamestate, use more recent frame
        if gamestate[0] < msg[0]:
            gamestate = msg
        elif gamestate[0] == msg[0]: # if sync is equal update only your clients info, not opponents info
            temp = list(gamestate)
            temp[1 + playerNum] = msg[1 + playerNum]
            temp[3 + playerNum] = msg[3 + playerNum]
            temp[5 + playerNum] = msg[5 + playerNum]
            gamestate = tuple(temp)

        currClient.send(compile_msg(gamestate).encode())
        
        gamelock.release()
        #========= END CRITICAL SECTION =========
        
    #close connection
    currClient.close()


# Create the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_IP, PORT))

# Wait for client connections
server.listen(5)
print(f"Server listening on port {PORT}")
print(f"Server info:{server.getsockname()}")

# Client 1 connects as Player 1
clientSocket, clientAddr = server.accept()
print(f"Client {clientAddr} connected")
firstClient = threading.Thread(target=client_handler, args = (clientSocket, 0))
print("Player 1 connected, waiting for second player")

# Client 2 connects as Player 2
clientSocket, clientAddr = server.accept()
print(f"Client {clientAddr} connected")
secondClient = threading.Thread(target=client_handler, args = (clientSocket, 1))
print("Player 2 connected, starting game")

# Start both client threads
firstClient.start()
secondClient.start()