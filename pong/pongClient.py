# =================================================================================================
# Contributing Authors:	    Caroline Waters & Alexander Wyatt
# Email Addresses:          cewa241@uky.edu, ajwy223@uky.edu
# Date:                     11/16/23
# Purpose:                  Implements the pong client. Communicates with server in tandem with
#                               another client to play a multiplayer pong game. 
# Misc:                     Although functional, does tend to experience some lag. We believe that
#                               this may be due to large discrepancies in sync status between the
#                               two clients. Causes ball to have somewhat unpredictable movement 
#                               when lag occurs in game and its position abruptly changes.
# =================================================================================================

import pygame
import tkinter as tk
import sys
import socket

from assets.code.helperCode import *

# Method responsible for sending and receiving the gamestate payload to and from the server.
def update_server(clientInfo:tuple, client:socket.socket) -> tuple:
    # send our gamestate to server
    try:
        client.send(compile_msg(clientInfo).encode())
    except:
        print("Failed to send an update to the server")
        
    # get most updated game state from server
    try:
        resp = client.recv(PAYLOAD_SIZE)
    except:
        print("Failed to receive a response from the server")
            
    return parse_msg(resp.decode())

# This is the main game loop.  For the most part, you will not need to modify this.  The sections
# where you should add to the code are marked.  Feel free to change any part of this project
# to suit your needs.
def playGame(screenWidth:int, screenHeight:int, playerPaddle:str, client:socket.socket) -> None:
    
    # Pygame inits
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()

    # Constants
    WHITE = (255,255,255)
    GRAY = (150,150,150)
    STARTFRAME = 180
    WIN_CON = 10
    clock = pygame.time.Clock()
    scoreFont = pygame.font.Font("./assets/fonts/pong-score.ttf", 32)
    winFont = pygame.font.Font("./assets/fonts/visitor.ttf", 48)
    pointSound = pygame.mixer.Sound("./assets/sounds/point.wav")
    bounceSound = pygame.mixer.Sound("./assets/sounds/bounce.wav")

    # Display objects
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    winMessage = pygame.Rect(0,0,0,0)
    topWall = pygame.Rect(-10,0,screenWidth+20, 10)
    bottomWall = pygame.Rect(-10, screenHeight-10, screenWidth+20, 10)
    centerLine = []
    for i in range(0, screenHeight, 10):
        centerLine.append(pygame.Rect((screenWidth/2)-5,i,5,5))

    # Paddle properties and init
    paddleHeight = 100
    paddleWidth = 10
    paddleStartPosY = (screenHeight/2)-(paddleHeight/2)
    leftPaddle = Paddle(pygame.Rect(10,paddleStartPosY, paddleWidth, paddleHeight))
    rightPaddle = Paddle(pygame.Rect(screenWidth-20, paddleStartPosY, paddleWidth, paddleHeight))

    ball = Ball(pygame.Rect(screenWidth/2, screenHeight/2, 5, 5), -5, 0)

    #determine whose side is whose
    if playerPaddle == "left":
        opponentPaddleObj = rightPaddle
        playerPaddleObj = leftPaddle
    else:
        opponentPaddleObj = leftPaddle
        playerPaddleObj = rightPaddle

    lScore = 0
    rScore = 0

    sync = 0
    
    while True:
        # Wiping the screen
        screen.fill((0,0,0))

        # Getting keypress events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    playerPaddleObj.moving = "down"

                elif event.key == pygame.K_UP:
                    playerPaddleObj.moving = "up"

            elif event.type == pygame.KEYUP:
                playerPaddleObj.moving = ""
        # =========================================================================================
        # Your code here to send an update to the server on your paddle's information,
        # where the ball is and the current score.
        # Feel free to change when the score is updated to suit your needs/requirements
        
        #clientUpdate format:
        #sync, lScore, rScore, lpaddle y, rpaddle y, lpaddle moving, rpaddle moving, ball x, ball y, ball vx, ball vy
        #0   , 1     , 2     , 3        , 4        , 5             , 6             , 7     , 8     , 9      , 10
        clientUpdate = [sync, lScore, rScore, leftPaddle.rect.y, rightPaddle.rect.y, leftPaddle.moving, rightPaddle.moving, ball.rect.x, ball.rect.y, ball.xVel, ball.yVel]
        
        serverStatus = update_server(clientUpdate, client)
        
        if playerPaddle == "left":
            opponentPaddleObj.moving = serverStatus[6]
        else:
            opponentPaddleObj.moving = serverStatus[5]
        
        # =========================================================================================

        # Update the player paddle and opponent paddle's location on the screen
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            if paddle.moving == "down":
                if paddle.rect.bottomleft[1] < screenHeight-10:
                    paddle.rect.y += paddle.speed
            elif paddle.moving == "up":
                if paddle.rect.topleft[1] > 10:
                    paddle.rect.y -= paddle.speed


        # Drawing the dotted line in the center
        for i in centerLine:
            pygame.draw.rect(screen, GRAY, i)
            
        # If the game is over, display the win message
        if lScore > WIN_CON or rScore > WIN_CON:
            winText = "Player 1 Wins! " if lScore > 4 else "Player 2 Wins! "
            textSurface = winFont.render(winText, False, WHITE, (0,0,0))
            textRect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2)
            winMessage = screen.blit(textSurface, textRect)
        elif sync > STARTFRAME: # don't display the ball while counting down

            # ==== Ball Logic =====================================================================
            ball.updatePos()

            # If the ball makes it past the edge of the screen, update score, etc.
            if ball.rect.x > screenWidth:
                lScore += 1
                pointSound.play()
                ball.reset(nowGoing="left")
            elif ball.rect.x < 0:
                rScore += 1
                pointSound.play()
                ball.reset(nowGoing="right")
                
            # If the ball hits a paddle
            if ball.rect.colliderect(playerPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(playerPaddleObj.rect.center[1])
            elif ball.rect.colliderect(opponentPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(opponentPaddleObj.rect.center[1])
                
            # If the ball hits a wall
            if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
                bounceSound.play()
                ball.hitWall()
            
            pygame.draw.rect(screen, WHITE, ball)
            # ==== End Ball Logic =================================================================
        
        # Display countdown for the first 4 seconds of the game
        if sync < (STARTFRAME/3):
            winText = "3"
        elif sync < (2*STARTFRAME/3):
            winText = "2"
        elif sync < (STARTFRAME):
            winText = "1"
        elif sync < (STARTFRAME + (STARTFRAME/3)):
            winText = "GO!"
            
            
        if sync <= (STARTFRAME + (STARTFRAME/3)):
            textSurface = winFont.render(winText, False, WHITE, (0,0,0))
            textRect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2)
            winMessage = screen.blit(textSurface, textRect)
            
        
        # Drawing the player's new location
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            pygame.draw.rect(screen, WHITE, paddle)

        pygame.draw.rect(screen, WHITE, topWall)
        pygame.draw.rect(screen, WHITE, bottomWall)
        scoreRect = updateScore(lScore, rScore, screen, WHITE, scoreFont)

        pygame.display.update()
        clock.tick(60)
        
        # This number should be synchronized between you and your opponent.  If your number is larger
        # then you are ahead of them in time, if theirs is larger, they are ahead of you, and you need to
        # catch up (use their info)
        # sync += 1
        # =========================================================================================
        # Send your server update here at the end of the game loop to sync your game with your
        # opponent's game

        clientUpdate = [sync, lScore, rScore, leftPaddle.rect.y, rightPaddle.rect.y, leftPaddle.moving, rightPaddle.moving, ball.rect.x, ball.rect.y, ball.xVel, ball.yVel]

        serverStatus = update_server(clientUpdate, client)

        # ======== UPDATING CLIENT USING THE SERVER DATA =============================================
        #update sync to whatever is most current
        sync = serverStatus[0]
 
        #Update to current score from the server
        lScore = serverStatus[1]
        rScore = serverStatus[2]
            
        # Update the player paddle and opponent paddle's location on the screen
        if playerPaddle == "left":
            opponentPaddleObj.rect.y = serverStatus[4]
        else:
            opponentPaddleObj.rect.y = serverStatus[3]

        # If the game is over, display the win message
        if lScore > WIN_CON or rScore > WIN_CON:
            winText = "Player 1 Wins! " if lScore > 4 else "Player 2 Wins! "
            textSurface = winFont.render(winText, False, WHITE, (0,0,0))
            textRect = textSurface.get_rect()
            textRect.center = ((screenWidth/2), screenHeight/2)
            winMessage = screen.blit(textSurface, textRect)
        elif sync > STARTFRAME:

            # ==== Ball Logic =====================================================================
            ball.xVel = serverStatus[9]
            ball.yVel = serverStatus[10]
            ball.rect.x = serverStatus[7]
            ball.rect.y = serverStatus[8]
            ball.updatePos()

            # If the ball makes it past the edge of the screen, update score, etc.
            if ball.rect.x > screenWidth:
                lScore += 1
                pointSound.play()
                ball.reset(nowGoing="left")
            elif ball.rect.x < 0:
                rScore += 1
                pointSound.play()
                ball.reset(nowGoing="right")
                
            # If the ball hits a paddle
            if ball.rect.colliderect(playerPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(playerPaddleObj.rect.center[1])
            elif ball.rect.colliderect(opponentPaddleObj.rect):
                bounceSound.play()
                ball.hitPaddle(opponentPaddleObj.rect.center[1])
                
            # If the ball hits a wall
            if ball.rect.colliderect(topWall) or ball.rect.colliderect(bottomWall):
                bounceSound.play()
                ball.hitWall()
            
            pygame.draw.rect(screen, WHITE, ball)
            # ==== End Ball Logic =================================================================

        # Drawing the player's new location
        for paddle in [playerPaddleObj, opponentPaddleObj]:
            pygame.draw.rect(screen, WHITE, paddle)

        pygame.draw.rect(screen, WHITE, topWall)
        pygame.draw.rect(screen, WHITE, bottomWall)
        scoreRect = updateScore(lScore, rScore, screen, WHITE, scoreFont)
        
        pygame.display.update()
        sync += 1
        #===== END UPDATE USING SERVER DATA ===========================================================




# This is where you will connect to the server to get the info required to call the game loop.  Mainly
# the screen width, height and player paddle (either "left" or "right")
# If you want to hard code the screen's dimensions into the code, that's fine, but you will need to know
# which client is which
def joinServer(ip:str, port:str, errorLabel:tk.Label, app:tk.Tk) -> None:
    # Purpose:      This method is fired when the join button is clicked
    # Arguments:
    # ip            A string holding the IP address of the server
    # port          A string holding the port the server is using
    # errorLabel    A tk label widget, modify it's text to display messages to the user (example below)
    # app           The tk window object, needed to kill the window
    
    # Create a socket and connect to the server
    # You don't have to use SOCK_STREAM, use what you think is best
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, int(port)))

    # Get the required information from your server (screen width, height & player paddle, "left or "right)
    resp = client.recv(PAYLOAD_SIZE)
    my_side = resp.decode()

    # If you have messages you'd like to show the user use the errorLabel widget like so
    errorLabel.config(text=f"Some update text. You input: IP: {ip}, Port: {port}")
    # You may or may not need to call this, depending on how many times you update the label
    errorLabel.update()     

    # Close this window and start the game with the info passed to you from the server
    app.withdraw()     # Hides the window (we'll kill it later)
    playGame(960, 720, my_side, client)  # User will be either left or right paddle
    app.quit()         # Kills the window
    client.close()


# This displays the opening screen, you don't need to edit this (but may if you like)
def startScreen():
    app = tk.Tk()
    app.title("Server Info")

    image = tk.PhotoImage(file="./assets/images/logo.png")

    titleLabel = tk.Label(image=image)
    titleLabel.grid(column=0, row=0, columnspan=2)

    ipLabel = tk.Label(text="Server IP:")
    ipLabel.grid(column=0, row=1, sticky="W", padx=8)

    ipEntry = tk.Entry(app)
    ipEntry.grid(column=1, row=1)

    portLabel = tk.Label(text="Server Port:")
    portLabel.grid(column=0, row=2, sticky="W", padx=8)

    portEntry = tk.Entry(app)
    portEntry.grid(column=1, row=2)

    errorLabel = tk.Label(text="")
    errorLabel.grid(column=0, row=4, columnspan=2)

    joinButton = tk.Button(text="Join", command=lambda: joinServer(ipEntry.get(), portEntry.get(), errorLabel, app))
    joinButton.grid(column=0, row=3, columnspan=2)

    app.mainloop()

if __name__ == "__main__":
    startScreen()
