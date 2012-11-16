import csv
from OpenGL.GL import *
import pygame

import levelobj
from textureatlas import *
from textbox import *

class Level(object):
  """A level"""

  levelDir = "../assets/levels/"

  def __init__(self, ui, levelFile):
    self.__ui = ui
    self._height = 0
    self._width = 0
    self._objects = [ [] ]
    self._startPos = (0, 0)
    self._doorPos = (0, 0)
    self.spritesheet = TileSet("../assets/", "spritesheet")
    self.charset = CharacterSet("../assets/font.png")
    self.load(levelFile)

    self._text = TextEditor((0, 5.75), (32, 48), self.charset,
                            "This is some text.\nIt's not pretty.\n...but.")

    # Spawn a player
    self._player = levelobj.Player(self._startPos, self.spritesheet)

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
      objects = []
      for y, row in enumerate(csvFile):
        # Update the level's dimensions
        self._height += 1
        if len(row) > self._width:
          self._width = len(row)

        # Add the elements at each cell to a temporary representation
        for x, cell in enumerate(row):
          objects.append(levelobj.NAMES.get(cell,
            levelobj.LevelObject)((x,y), self.spritesheet))

      # Resize the self._objects to the size of the level
      self._objects = [[levelobj.LevelObject((x,y), self.spritesheet)
                        for y in xrange(self._height)]
                        for x in xrange(self._width)]

      for obj in objects:
        # Invert the y position
        obj.move((obj._pos[0], self._height - obj._pos[1]))

        # Get the start position
        if isinstance(obj, levelobj.Start):
          self._startPos = obj._pos

        # Get the door position
        if isinstance(obj, levelobj.Door):
          self._doorPos = obj._pos

        # Convert the temporary objects to the 2D list self._objects
        self._objects[int(obj._pos[0])-1][int(obj._pos[1])-1] = obj


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
          break

        # Temporary screen move stuff, trigger with right alt
        elif pygame.key.get_mods() & pygame.KMOD_RALT:
          if e.key == pygame.K_LEFT:
            self.x -= 0.5
          elif e.key == pygame.K_RIGHT:
            self.x += 0.5
          elif e.key == pygame.K_UP:
            self.y += 0.5
          elif e.key == pygame.K_DOWN:
            self.y -= 0.5
          elif e.key == pygame.K_w:
            self.xrot -= 5
          elif e.key == pygame.K_s:
            self.xrot += 5
          elif e.key == pygame.K_a:
            self.yrot -= 5
          elif e.key == pygame.K_d:
            self.yrot += 5
          elif e.key == pygame.K_i:
            pass
          elif e.key == pygame.K_j:
            self._player.relMove(self, (-1, 0))
          elif e.key == pygame.K_k:
            pass
          elif e.key == pygame.K_l:
            self._player.relMove(self, (1, 0))

        else:
          # Send all other keypresses to the text editor
          self._text.handleKeyPress(e.key, e.unicode)
    return False

  def draw(self, time):
    """Render the level interface."""
    # Draw
    glClearColor(0, 0, 1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Temporary screen move stuff
    glTranslate(self.x, self.y, 0)
    glRotate(self.xrot, 1, 0, 0)
    glRotate(self.yrot, 0, 1, 0)

    # Draw the static level
    for row in self._objects:
      for block in row:
        block.draw()

    # Draw the movable objects
    self._player.draw()

    # Draw the editor
    self._text.draw()
