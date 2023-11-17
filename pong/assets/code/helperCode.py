# You don't need to edit this file at all unless you really want to
import pygame

# This draws the score to the screen
def updateScore(lScore:int, rScore:int, screen:pygame.surface.Surface, color, scoreFont:pygame.font.Font) -> pygame.Rect:
    textSurface = scoreFont.render(f"{lScore}   {rScore}", False, color)
    textRect = textSurface.get_rect()
    screenWidth = screen.get_width()
    textRect.center = ((screenWidth/2)+5, 50)
    return screen.blit(textSurface, textRect)

class Paddle:
    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect
        self.moving = ""
        self.speed = 5

class Ball:
    def __init__(self, rect:pygame.Rect, startXvel:int, startYvel:int) -> None:
        self.rect = rect
        self.xVel = startXvel
        self.yVel = startYvel
        self.startXpos = rect.x
        self.startYpos = rect.y
    
    def updatePos(self) -> None:
        self.rect.x += self.xVel
        self.rect.y += self.yVel
    
    def hitPaddle(self, paddleCenter:int) -> None:
        self.xVel *= -1
        self.yVel = (self.rect.center[1] - paddleCenter)//2
    
    def hitWall(self) -> None:
        self.yVel *= -1
    
    def reset(self, nowGoing:str) -> None:
        # nowGoing  The direction the ball should be going after the reset
        self.rect.x = self.startXpos
        self.rect.y = self.startYpos
        self.xVel = -5 if nowGoing == "left" else 5
        self.yVel = 0
        
# This function parses a string that follows our standardized formatting
# and returns the output as a list.
def parse_msg(inString:str) -> tuple:
    #split string using comma as the delimiter
    inString = inString.split(",")
    
    #The following line is the standard format
    #sync, lScore, rScore, lpaddle y, rpaddle y, ball x, ball y, ball vx, ball vy
    return int(inString[0]), int(inString[1]), int(inString[2]), int(inString[3]), int(inString[4]), int(inString[5]), int(inString[6]), int(inString[7]), int(inString[8])

# This function takes a list in our standard format and returns
# a string with that data in our standard format.
def compile_msg(toSend: tuple) -> str:
    # Have to process the first data entry separately to ensure appropriate number of commas
    result = str(toSend[0])
    for i in range(1, 9):
        result += "," + str(toSend[i])
    
    return result
