# =================================================================================================
# Contributing Authors:	    Alexander Wyatt
# Email Addresses:          ajwy223@uky.edu
# Date:                     11/1/2023
# Purpose:                  <How this file contributes to the project>
# Misc:                     <Not Required.  Anything else you might want to include>
# =================================================================================================

import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(("localhost",12321))
server.listen(5)

# Use this file to write your server logic
# You will need to support at least two clients
# You will need to keep track of where on the screen (x,y coordinates) each paddle is, the score 
# for each player and where the ball is, and relay that to each client
# I suggest you use the sync variable in pongClient.py to determine how out of sync your two
# clients are and take actions to resync the games