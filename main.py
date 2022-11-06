from cmu_112_graphics import *
import math, copy, random
import floorplan as fp
import floorPlanList as fpl
import testmap as tp
'''
Changelog (Emily woke up at 7:00 and fucked around):
Pause menu added
Kai now exists (as a bisque circle) and can move
Some rat bugs fixed (TODO: actually spawn and draw the rats)
TODO: game balancing once we do start spawning rats
TODO: make game look good
TODO: gut the edit controls menu
'''
################################################################################
#
# CLASSES
#
################################################################################

class Player:
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.inventory = dict()

    def drawPlayer(self, app, canvas):
        if 0 <= self.row < app.rows and 0 <= self.col < app.cols:
            # TODO: canvas.create_circle. idk how to do this
            x0, y0, x1, y1 = getCellBounds(app, self.row, self.col)
            margin = app.width*0.001
            canvas.create_oval(x0+margin, y0+margin, x1-margin, y1-margin, fill='bisque2')
    
    def movePlayer(self, app, drow, dcol): 
        # TODO: finish this when the map is stored in app
        if not ((self.row + drow < 0) or (self.row + drow >= app.rows) or (self.col + dcol < 0) or (self.col + dcol >= app.cols)):
            self.row += drow
            self.col += dcol

            if not self.legalMove(app):
                self.row -= drow
                self.col -= dcol

    def legalMove(self, app):
        if app.map[self.row][self.col] is False:
            return False
        return True

    def getItem(self, app, item): # or something like this
        self.inventory[item] = self.inventory.get(item, 0)
        self.inventory[item] += 1

class Button:
    buttonList = list()
    def __init__(self, cornX, cornY, width, height, label, fill='bisque2'):
        self.cornX, self.cornY = cornX, cornY
        self.width, self.height = width, height
        self.fill = fill
        self.label = label
        Button.buttonList.append(self)
        self.isVisible = False

    def __repr__(self):
        return f'{self.label} at ({self.cornX}, {self.cornY})'

    def drawButton(self, app, canvas):
        self.isVisible = True
        fontSize = int(0.1*self.width)
        canvas.create_rectangle(self.cornX, self.cornY, self.cornX + self.width, self.cornY + self.height, 
        fill = self.fill)
        canvas.create_text(self.cornX+self.width/2, self.cornY+self.height/2, font = f'arial {fontSize}', text = self.label)

    @staticmethod
    def getButton(app, event):
        mouseX, mouseY = event.x, event.y
        for button in Button.buttonList:
            if (button.cornX <= mouseX <= button.cornX+button.width and 
                button.cornY <= mouseY <= button.cornY + button.height):
                if button.isVisible:
                    print(button)
                    return button
        return None

class Controls:
    def __init__(self):
        self.moveUp = 'w'
        self.moveLeft = 'a'
        self.moveRight = 'd'
        self.moveDown = 's'
        self.interact = 'space'
        self.inventory = 'e' # like in Minecraft!!!
        self.back = 'escape'
        self.confirm = ['enter', self.interact, self.inventory] # either one of these shall work as confirm
        # V this is used for checking if a key is already used?
        self.boundKeys = {self.moveLeft, self.moveUp, self.moveRight, 
                          self.moveDown, self.interact, self.inventory, 
                          self.back, *self.confirm}

    def createControlButtons(self, app): # for the settings menu
        # sorry. This is awful.
        # Button drawings don't update after editing controls for some reason
        # TODO: GO TO OH AHHHHHHH
        width, height = 150, 50
        cornX, cornY = app.width/2 - 1.15*width, app.height*0.32
        dy = height + app.height*0.02
        app.changeUp = cButton(cornX, cornY, width, height,
                              f'up: {app.controls.moveUp}', app.controls.moveUp)
        app.changeLeft = cButton(cornX, cornY + dy, width, height,
                                f'left: {self.moveLeft}', app.controls.moveLeft)
        app.changeRight = cButton(cornX, cornY + 2*dy, width, height,
                                 f'right: {self.moveRight}', app.controls.moveRight)
        app.changeDown = cButton(cornX, cornY + 3*dy, width, height,
                                f'down: {self.moveDown}', app.controls.moveDown)
        cornX = app.width/2 + .15*width
        app.changeInteract = cButton(cornX, cornY, width, height,
                                    f'interact: {self.interact}', app.controls.interact)
        app.changeInventory = cButton(cornX, cornY + dy, width, height,
                                     f'inventory: {self.inventory}', app.controls.inventory)
        app.changeBack = cButton(cornX, cornY + 2*dy, width, height,
                                f'back: {self.back}', app.controls.back)
        app.changeConfirm = cButton(cornX, cornY + 3*dy, width, height,
                                   f'confirm: {self.confirm[0]}', app.controls.confirm)
        app.controlButtons = [app.changeUp, app.changeLeft, app.changeRight, 
                              app.changeDown, app.changeInteract, 
                              app.changeInventory, app.changeBack, 
                              app.changeConfirm]

class cButton(Button): # controlButton
    def __init__(self, cornX, cornY, width, height, label, control):
        super().__init__(cornX, cornY, width, height, label, fill='bisque2')
        self.control = control

    def editControls(self, app, key):
        self.control = key
        if 'up' in self.label:
            app.controls.moveUp = self.control
        elif 'down' in self.label:
            app.controls.moveDown = self.control
        elif 'right' in self.label:
            app.controls.moveRight = self.control
        elif 'left' in self.label:
            app.controls.moveLeft = self.control
        elif 'interact' in self.label:
            app.controls.interact = self.control
        elif 'inventory' in self.label:
            app.controls.inventory = self.control
        elif 'confirm' in self.label:
            app.controls.confirm = [self.control, app.controls.interact, app.controls.inventory]
        app.editedControl = None

    def drawControlMenu(self, app, canvas):
        # draw a rectangle
        pass

class Rat(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        initLvl = 3
        self.speedLvl = initLvl
        initXDir = random.randint(-1, 2)
        initYDir = random.randint(-1, 2)
        self.direction = (initXDir, initYDir)

    def isLegalMove(self, app, x, y):
        if x >= app.cols or y >= app.rows:
            return False
        if app.map[x][y] == True:
            return False
        return True

    def moveRat(self, app):
        self.x += self.direction[0]
        self.y += self.direction[1]
        if not self.isLegalMove(app, self.x, self.y):
            self.x -= self.direction[0]
            self.y -= self.direction[1]

# 🐀

def spawnRat(app):
    x = random.randint(0, app.rows-1)
    y = random.randint(0, app.cols-1)
    if app.map[x][y]==False:
        app.mischief.append(Rat(x, y))

def timerFired(app):
    if not app.paused and app.currScreen == 'game':
        for rat in app.mischief:
            rat.moveRat(app)
        if app.timerCount % 10 == 0:
            spawnRat(app)
    
    app.timerCount += 1
################################################################################
#
# NOT CLASSES
#
################################################################################

def appStarted(app):
    app.currScreen = 'splash'
    app.prevScreen = list()
    app.prevScreen.append(app.currScreen)
    app.map = tp.testmap
    app.rows = len(app.map)
    app.cols = len(app.map[0])
    app.margin = 5
    app.startButton = Button(app.width/2-75, app.height*0.57, 150, 80, 'start')
    app.creditsButton = Button(app.width/2-75, app.height*0.83, 150, 80, 'credits')
    app.settingsButton = Button(app.width/2-75, app.height*0.7, 150, 80, 'settings')
    app.backButton = Button(30, app.height - 60, 80, 40, 'back')
    app.controls = Controls()
    app.controls.createControlButtons(app)
    app.editedControl = None
    app.mischief = []
    app.timerDelay = 100
    app.timerCount = 0
    app.kai = Player(2, 2)
    app.paused = True


################################################################################
#
# GRAPHICS
#
################################################################################
def redrawAll(app, canvas):
    if app.currScreen == 'splash':
        drawSplashScreen(app, canvas)
    elif app.currScreen == 'game':
        drawGameScreen(app, canvas)
        if app.paused == True:
            drawPauseScreen(app, canvas)
    elif app.currScreen == 'credits':
        drawCreditsScreen(app, canvas)
    elif app.currScreen == 'settings':
        drawSettingsScreen(app, canvas)
        if app.editedControl:
            app.editedControl.drawControlMenu(app, canvas)


def drawSplashScreen(app, canvas):
    # draw Donner
    introFontSize = 40
    canvas.create_text(app.width/2, 300, font=f'Arial {introFontSize} bold',
        text='Escape Donner Dungeon')
    app.creditsButton.drawButton(app, canvas)
    app.settingsButton.drawButton(app, canvas)
    app.startButton.drawButton(app, canvas)

def drawCreditsScreen(app, canvas):
    # TODO: write when we're basically done
    canvas.create_text(app.width/2, app.height/2 - 0.35*app.height, 
                       font='Arial 40 bold', text='Credits')
    canvas.create_text(app.width/2, app.height/2 - 0.25*app.height, 
                       font='Arial 20', text='andrewIDs')
    app.backButton.drawButton(app, canvas)

def drawSettingsScreen(app, canvas):
    canvas.create_text(app.width/2, app.height/2 - 0.35*app.height, 
                       font='Arial 40 bold', text='Settings')
    for button in app.controlButtons:
        button.drawButton(app, canvas)
    app.backButton.drawButton(app, canvas)

def drawGameScreen(app, canvas):
    drawBoard(app, canvas)
    app.kai.drawPlayer(app, canvas)

def drawPauseScreen(app, canvas):
    margin = app.width*0.05
    canvas.create_rectangle(margin, margin, app.width-margin, app.height-margin, fill='bisque')
    canvas.create_text(app.width/2, margin+app.height*0.06, font='Arial 20', text='Paused')
    resumeButton = Button(app.width/2-0.18*app.width, app.height/2 - 70, 0.36*app.width, 90, 'resume')
    resumeButton.drawButton(app, canvas)
    exitGame = Button(app.width/2-0.18*app.width, app.height/2 + 40, 0.36*app.width, 90, 'menu')
    exitGame.drawButton(app, canvas)
    app.settingsButton.drawButton(app, canvas)
    app.creditsButton.drawButton(app, canvas)
    app.backButton.drawButton(app, canvas)

def mouseMoved(app, event):
    pass
    # trying to highlight a button when you hover over it
    # struggling to uncolor the button
    # start a timer to unhighlight the button instead?
    # highlightedButton = Button.getButton(app, event)
    # pastButton = app.backButton
    # if highlightedButton != None:
    #     pastButton = highlightedButton
    #     print(pastButton)
    #     highlightedButton.fill = 'bisque'
    # else:
    #     pastButton.fill = 'bisque2'

def mousePressed(app, event):
    buttonPressed = Button.getButton(app, event)
    if buttonPressed != None:
        buttonName = buttonPressed.label.lower()
        for button in Button.buttonList:
            button.isVisible = False
        if buttonName == 'back' and len(app.prevScreen) != 0: # should work for whatever 
            # TODO: properly update app.prevScreen
            app.currScreen = app.prevScreen[-1]
        if app.currScreen == 'splash':
            # pressing the buttons that are on the splashscreen
            if buttonName == 'start':
                app.paused = False
                app.currScreen = 'game'
            elif buttonName == 'settings':
                app.currScreen = 'settings'
            elif buttonName == 'credits':
                app.currScreen = 'credits'
        elif app.currScreen == 'settings':
            if isinstance(buttonPressed, cButton) and buttonPressed != None:
                event.key = None
                app.editedControl = buttonPressed
        elif app.currScreen == 'game':
            if buttonName == 'resume':
                app.paused = False
            elif buttonName == 'settings':
                app.currScreen = 'settings'
            elif buttonName == 'credits':
                app.currScreen = 'credits'
            elif buttonName == 'menu':
                app.prevScreen.append('splash')
                app.currScreen = 'splash'
        if not app.currScreen == 'game':
            app.paused = True


def keyPressed(app, event):
    key = event.key.lower() # use key so we don't have to worry about capitalization
    if key == 'escape':
        print(app.paused)
    if not app.paused and app.currScreen == 'game':
        if key == 'w':
            app.kai.movePlayer(app, -1, 0)
        elif key == 'a':
            app.kai.movePlayer(app, 0, -1)
        elif key == 's':
            app.kai.movePlayer(app, 1, 0)
        elif key == 'd':
            app.kai.movePlayer(app, 0, 1)
        elif key == 'escape':
            app.paused = True
            app.prevScreen.append('game')
    elif app.paused and app.currScreen == 'game':
        if key == 'escape':
            app.paused = False
    elif key == 'escape' and len(app.prevScreen) != 0: # go back. might be fucky if this is also used to close inventory IDFK
        app.currScreen = app.prevScreen[-1]
    elif app.currScreen == 'settings' and app.editedControl:
        app.editedControl.editControls(app, key)


def drawBoard(app, canvas):
    for row in range(app.rows):
        for col in range(app.cols):
            if app.map[row][col] == False:
                drawCell(app, canvas, row, col,'blue')
            else:
                drawCell(app,canvas,row,col,'white')

def getCellBounds(app, row, col):
    # aka "modelToView"
    # returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth = gridWidth / app.cols
    cellHeight = gridHeight / app.rows
    x0 = app.margin + col * cellWidth
    x1 = app.margin + (col+1) * cellWidth
    y0 = app.margin + row * cellHeight
    y1 = app.margin + (row+1) * cellHeight
    return (x0, y0, x1, y1)
    
def gameDimensions():
    rows = 150
    cols = 100
    cellSize = 2
    margin = 1
    return (rows, cols, cellSize, margin)

def drawCell(app, canvas, row, col, colour):
    if colour == None:
        x0, y0, x1, y1 = getCellBounds(app, row, col)
        canvas.create_rectangle(x0, y0, x1, y1, fill=app.board[row][col],
                                outline='black', width=4)
    else:
        x0, y0, x1, y1 = getCellBounds(app, row, col)
        canvas.create_rectangle(x0,y0, x1, y1, fill=colour,outline='black', 
                                width=4)

# def getCell(app, x, y):
#     # aka "viewToModel"
#     # return (row, col) in which (x, y) occurred or (-1, -1) if outside grid.
#     if (not pointInGrid(app, x, y)):
#         return (-1, -1)
#     gridWidth  = app.width - 2*app.margin
#     gridHeight = app.height - 2*app.margin
#     cellWidth  = gridWidth / app.cols
#     cellHeight = gridHeight / app.rows

#     # Note: we have to use int() here and not just // because
#     # row and col cannot be floats and if any of x, y, app.margin,
#     # cellWidth or cellHeight are floats, // would still produce floats.
#     row = int((y - app.margin) / cellHeight)
#     col = int((x - app.margin) / cellWidth)
#     return (row, col)

def main():
    runApp(width=720, height=720)

main()