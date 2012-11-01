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

    # Temporary screen move stuff
    self.t = 0.0
    self.x = 0.0
    self.y = 0.0
    self.xrot = 0.0
    self.yrot = 0.0
    self.botx = 0
    self.botz = 1

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

        # Temporary screen move stuff
        elif e.key == pygame.K_LEFT:
          self.x -= 0.05
        elif e.key == pygame.K_RIGHT:
          self.x += 0.05
        elif e.key == pygame.K_UP:
          self.y += 0.05
        elif e.key == pygame.K_DOWN:
          self.y -= 0.05
        elif e.key == pygame.K_w:
          self.xrot -= 0.5
        elif e.key == pygame.K_s:
          self.xrot += 0.5
        elif e.key == pygame.K_a:
          self.yrot -= 0.5
        elif e.key == pygame.K_d:
          self.yrot += 0.5
        elif e.key == pygame.K_i:
          self.botz -= 0.01
        elif e.key == pygame.K_j:
          self.botx -= 0.01
        elif e.key == pygame.K_k:
          self.botz += 0.01
        elif e.key == pygame.K_l:
          self.botx += 0.01
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

    # Temporary screen move stuff
    glTranslate(self.x, self.y, 0)
    glRotate(self.xrot, 1, 0, 0)
    glRotate(self.yrot, 0, 1, 0)

    for block in self._objects:
      block.draw()
