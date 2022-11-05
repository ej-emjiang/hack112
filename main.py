from cmu_112_graphics import *
import math, copy
import floorplan as fp

################################################################################
#
# CLASSES
#
################################################################################

class Player:
    def __init__(self, row, col):
        self.row, self.col = row, col
        self.inventory = dict()
    
    def movePlayer(self, app, drow, dcol): 
        # TODO: finish this when the map is stored in app
        targetRow, targetCol = self.row + drow, self.col + dcol

    def getItem(self, app, item): # or something like this
        self.inventory[item] = self.inventory.get(item, 0)
        self.inventory[item] += 1

class Button:
    buttonList = list()
    def __init__(self, cornX, cornY, width, height, label):
        self.cornX, self.cornY = cornX, cornY
        self.width, self.height = width, height
        self.label = label
        Button.buttonList.append(self)

    def __repr__(self):
        return f'{self.label} at ({self.cornX}, {self.cornY})'

    def drawButton(self, app, canvas):
        # can someone draw me a rectangle with self.label written in the center uwu
        fontSize = int(0.1*self.width)
        canvas.create_rectangle(self.cornX, self.cornY, self.cornX + self.width, self.cornY + self.height, 
        fill = 'bisque2')
        canvas.create_text(self.cornX+self.width/2, self.cornY+self.height/2, font = f'arial {fontSize}', text = self.label)

    @staticmethod
    def getButton(app, event):
        mouseX, mouseY = event.x, event.y
        for button in Button.buttonList:
            if (button.cornX <= mouseX <= button.cornX+button.width and 
                button.cornY <= mouseY <= button.cornY + button.height):
                return button.label.lower()
        return None

# class Screen: # idfk what to do here.
    # def __init__(self, name, buttons):
    #     self.name = name
    #     self.buttons = buttons # list of buttons

    # def __repr__(self):
    #     return self.name

    # def __eq__(self, other):
    #     return isinstance(other, Screen) and self.name == other.name

    # def drawScreen(self, app, canvas):
    #     pass

    # @staticmethod
    # def initializeScreens(app):
    #     result = list()
    #     splash = initializeSplash(app)
    #     options = initializeOptions(app)
    #     credits = initializeCredits(app)
    #     game = initializeGame(app)

    # @staticmethod
    # def initializeSplash(app):

def appStarted(app):
    # app.screens = Screen.initializeScreens(app)
    app.currScreen = 'splash'
    app.prevScreen = list()
    app.prevScreen.append(app.currScreen)
    app.rows = 150
    app.cols = 100
    app.margin = 5
    app.testButton = Button(app.width-300, app.height/2+80, 200, 120, 'credits')
    app.backButton = Button(30, app.height - 60, 40, 20, 'back')
    loadControls(app)

def loadControls(app):
    app.moveLeft = 'a'
    app.moveRight = 'd'
    app.moveUp = 'w'
    app.moveDown = 's'
    app.interact = 'space'


################################################################################
#
# GRAPHICS
#
################################################################################
def redrawAll(app, canvas):
    if app.currScreen == 'splash':
        drawSplashScreen(app, canvas)
    elif app.currScreen == 'credits':
        drawCreditsScreen(app, canvas)

def drawSplashScreen(app, canvas):
    # draw Donner
    # draw title screen text
    # buttons for startgame, options, and credits?
    introFontSize = 40
    canvas.create_text(app.width/2, 300, font=f'Arial {introFontSize} bold',
        text='Escape Donner Dungeon')
    # canvas.create_rectangle(app.width-300, app.height/2+80, 
    #                         app.width - 200, app.height/2 + 120)
    app.testButton.drawButton(app, canvas)

def drawCreditsScreen(app, canvas):
    # TODO: write when we're basically done
    canvas.create_text(app.width/2, app.height/2 - 0.35*app.height, font='Arial 40 bold', text='Credits')
    canvas.create_text(app.width/2, app.height/2 - 0.25*app.height, font='Arial 20', text='andrewIDs')
    app.backButton.drawButton(app, canvas)

def mousePressed(app, event):
    buttonPressed = Button.getButton(app, event)
    if buttonPressed == 'back' and len(app.prevScreen) != 0: # should work for whatever 
        # TODO: properly update app.prevScreen
        app.currScreen = app.prevScreen[-1]
    if app.currScreen == 'splash':
        # pressing the buttons that are on the splashscreen
        if buttonPressed == 'start':
            app.currScreen = 'game'
        elif buttonPressed == 'settings':
            app.currScreen = 'settings'
        elif buttonPressed == 'credits':
            app.currScreen = 'credits'

def keyPressed(app, event):
    print(event.key)
    if app.currScreen == 'game': 
        # movement, interacting, etc. do event.key.lower() or whatever to account for accidental capslock
        pass


def getCell(app, x, y):
    # aka "viewToModel"
    # return (row, col) in which (x, y) occurred or (-1, -1) if outside grid.
    if (not pointInGrid(app, x, y)):
        return (-1, -1)
    gridWidth  = app.width - 2*app.margin
    gridHeight = app.height - 2*app.margin
    cellWidth  = gridWidth / app.cols
    cellHeight = gridHeight / app.rows

    # Note: we have to use int() here and not just // because
    # row and col cannot be floats and if any of x, y, app.margin,
    # cellWidth or cellHeight are floats, // would still produce floats.
    row = int((y - app.margin) / cellHeight)
    col = int((x - app.margin) / cellWidth)

    return (row, col)

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

def main():
    runApp(width=1280, height=720)

main()