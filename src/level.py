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
    self.spritesheet = levelobj.TileSet("../assets/", "spritesheet")
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
          self._objects.append(levelobj.NAMES.get(cell,
            levelobj.LevelObject)((x,y), self.spritesheet))
          # self._objects.append(levelobj.NAMES[cell]((x,y), self.spritesheet))

      print "Level: loaded", levelFile
      file.close()

  def handleEvents(self, events):
    """Handle keyboard input."""
    for e in events:
      if e.type == pygame.QUIT:
        return True
      elif e.type == pygame.KEYDOWN:
        if e.key == pygame.K_ESCAPE:
          self.__ui.popState()
    return False

  def draw(self):
    """Render the level interface."""
    # TODO: implement!
    # self.__ui.drawBackground(0, 1, 0)

    # Draw
    glClearColor(0, 0, 1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(0, 0, 0)
    # XXX glRotate(t / 40, 0, 1, -1)
    glRotate(0, 1, 0, 0)
    glRotate(0, 0, 1, 0)

    for block in self._objects:
      block.draw()
