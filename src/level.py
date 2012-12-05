import csv
from OpenGL.GL import *
import pygame

import c.error
import c.scanner
import c.parser
import c.tacgen
import vm.tactrans
import vm.bytecode

import levelobj
from textureatlas import *
from textbox import *

LEVEL_DIR = "assets/levels/"

class Level(object):
  """A level"""

  def __init__(self, ui, levelName):
    self.__ui = ui
    self._levelName = levelName
    self._height = 0
    self._width = 0
    self._objects = [ [] ]
    self.startPos = (0, 0)
    self.doorPos = (0, 0)

    # Load level assets
    self.spritesheet = self.__ui.spritesheet
    self.load(levelName)

  def load(self, levelName):
    """Load a level from a level base name."""
    with open(LEVEL_DIR + levelName + ".csv", 'rb') as levelfile:
      csvFile = csv.reader(levelfile)
      objects = []
      for y, row in enumerate(csvFile):
        # Update the level's dimensions
        self._height += 1
        if len(row) > self._width:
          self._width = len(row)

        # Add the elements at each cell to a temporary representation
        for x, cell in enumerate(row):
          objects.append(levelobj.NAMES.get(cell,
            levelobj.LevelObject)((x,y), self.spritesheet, self))

      # Resize the self._objects to the size of the level
      self._objects = [
        [
          levelobj.LevelObject((x, y), self.spritesheet, self)
            for y in xrange(self._height)
        ] for x in xrange(self._width)
      ]

      for obj in objects:
        # Invert the y position
        obj._pos = (obj._pos[0], self._height - obj._pos[1])

        # Get the start position
        if isinstance(obj, levelobj.Start):
          self.startPos = obj._pos

        # Get the door position
        if isinstance(obj, levelobj.Door):
          print "Door is at", obj._pos
          self.doorPos = obj._pos

        # Convert the temporary objects to the 2D list self._objects
        self._objects[int(obj._pos[0]) - 1][int(obj._pos[1]) - 1] = obj

  def at(self, pos):
    """Return the object at the given position."""
    return self._objects[pos[0] - 1][pos[1] - 1]

  def draw(self):
    """Render the level interface."""
    # Draw the static level
    for row in self._objects:
      for obj in row:
        obj.draw()
