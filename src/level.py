import csv
from OpenGL.GL import *
import pygame

import levelobj

class Level(object):
  """A level"""

  levelDir = "../assets/levels/"

  def __init__(self, ui, levelFile):
    self.__ui = ui
    self._height = 0
    self._width = 0
    self._objects = []
    self.load(levelFile)

  def load(self, levelFile):
    """Load a level from a CSV file."""
    with open(self.levelDir + levelFile, 'rb') as file:
      csvFile = csv.reader(file)
      for y, row in enumerate(csvFile):
        # Update the level's dimensions
        self._height += 1
        if len(row) > self._width:
          self._width = len(row)

        # Add the elements at each cell to the representation
        for x, cell in enumerate(row):
          # self._objects.append(levelobj.NAMES.get(cell,
          #   levelobj.LevelObject)((x,y)))
          self._objects.append(levelobj.NAMES[cell]((x,y)))

      print "Level: loaded", levelFile
      file.close()

  def userUp(self):
    print "Level: user up"

  def userDown(self):
    print "Level: user down"

  def userSelect(self):
    print "Level: user select"

  def userBack(self):
    print "Level: user back"
    self.__ui.popState()

  def draw(self):
    """Render the level interface."""
    # TODO: implement!
    self.__ui.drawBackground(0, 1, 0)
