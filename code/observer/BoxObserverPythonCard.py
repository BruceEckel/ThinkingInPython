# observer/BoxObserverPythonCard.py
""" Written by Kevin Altis as a first-cut for
converting BoxObserver to Python. The Observer
hasn't been integrated yet.
To run this program, you must:
Install WxPython from
http://www.wxpython.org/download.php
Install PythonCard. See:
http://pythoncard.sourceforge.net
"""
from PythonCardPrototype import log, model
import random

GRID = 8

class ColorBoxesTest(model.Background):
    def on_openBackground(self, event):
        self.document = []
        for row in range(GRID):
            line = []
            for column in range(GRID):
                line.append(self.createBox(row, column))
            self.document.append(line[:])
    def createBox(self, row, column):
        colors = ['black', 'blue', 'cyan',
        'darkGray', 'gray', 'green',
        'lightGray', 'magenta',
        'orange', 'pink', 'red',
        'white', 'yellow']
        width, height = self.panel.GetSizeTuple()
        boxWidth = width / GRID
        boxHeight = height / GRID
        log.info("width:" + str(width) +
          " height:" + str(height))
        log.info("boxWidth:" + str(boxWidth) +
          " boxHeight:" + str(boxHeight))
        # use an empty image, though some other
        # widgets would work just as well
        boxDesc = {'type':'Image',
          'size':(boxWidth, boxHeight), 'file':''}
        name = 'box-%d-%d' % (row, column)
        # There is probably a 1 off error in the
        # calculation below since the boxes should
        # probably have a slightly different offset
        # to prevent overlaps
        boxDesc['position'] = \
          (column * boxWidth, row * boxHeight)
        boxDesc['name'] = name
        boxDesc['backgroundColor'] = \
          random.choice(colors)
        self.components[name] =  boxDesc
        return self.components[name]

    def changeNeighbors(self, row, column, color):

        # This algorithm will result in changing the
        # color of some boxes more than once, so an
        # OOP solution where only neighbors are asked
        # to change or boxes check to see if they are
        # neighbors before changing would be better
        # per the original example does the whole grid
        # need to change its state at once like in a
        # Life program? should the color change
        # in the propogation of another notification
        # event?

        for r in range(max(0, row - 1),
                       min(GRID, row + 2)):
            for c in range(max(0, column - 1),
                           min(GRID, column + 2)):
                self.document[r][c].backgroundColor=color

    # this is a background handler, so it isn't
    # specific to a single widget. Image widgets
    # don't have a mouseClick event (wxCommandEvent
    # in wxPython)
    def on_mouseUp(self, event):
        target = event.target
        prefix, row, column = target.name.split('-')
        self.changeNeighbors(int(row), int(column),
                             target.backgroundColor)

if __name__ == '__main__':
    app = model.PythonCardApp(ColorBoxesTest)
    app.MainLoop()