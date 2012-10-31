import csv
from OpenGL.GL import *
import pygame

# TODO: implement the sprite atlas at "assets/spritesheet-0.png"
spriteDir = "../assets/sprites/"
class TileSet(object):
  """Holds the spritesheet for easy access"""

  def __init__(self, path, prefix):
    # TODO: handle multiple spritesheets
    
    # Parse the *.csv file
    self.__images = dict()
    with open(path + prefix + ".csv") as file:
      csvFile = csv.reader(file)
      for meta in csvFile:
        # Parse the individual element
        # Format: __images[sprite name] = (sheet file, top left corner, size)
        self.__images[meta[0]] = (meta[1], (int(meta[2]), int(meta[3])),
          (int(meta[4]), int(meta[5])))
      file.close()

    # Set up OpenGL
    # Picks a random sprite and assumes all other sprites have that size
    self.__tilew, self.__tileh = self.__images.itervalues().next()[2]
    self.__surface = pygame.image.load(path + prefix + "-0.png").convert_alpha()
    self.__w, self.__h = self.__surface.get_size()
    self.__es = 1.0 / self.__w
    self.__et = 1.0 / self.__h
    self.__htiles = self.__w / self.__tilew
    self.__vtiles = self.__h / self.__tileh
    self.__ntiles = self.__htiles * self.__vtiles
    self.__tex = glGenTextures(1)
    self.bindTexture()
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.__w, self.__h, 0, GL_RGBA,
      GL_UNSIGNED_BYTE, pygame.image.tostring(self.__surface, "RGBA", True))

  def bindTexture(self):
    """Tell OpenGL to use this spritesheet."""
    glBindTexture(GL_TEXTURE_2D, self.__tex)

  def tileCoord(self, spriteName, u, v):
    """Tell OpenGL to use this sprite."""
    s = self.__images[spriteName[0]][1][0] / self.__tilew
    t = self.__images[spriteName[0]][1][1] / self.__tileh
    assert s < self.__htiles
    assert t < self.__vtiles
    assert u >= 0.0 and u <= 1.0
    assert v >= 0.0 and v <= 1.0
    glTexCoord2f((s + u) * self.__tilew * self.__es,
      (self.__h - (t + 1.0 - v) * self.__tileh) * self.__et)

class LevelObject(object):
  """The base level object"""

  _dHealth = 0
  _blocking = False

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[0].append("default.png")

  def _uinit(self, pos, spritesheet):
    """Initialization common to all child classes."""
    self._pos = pos
    self._spritesheet = spritesheet
    # Format: 0 = front, 1 = back, 2 = top, 3 = bottom, 4 = left, 5 = right
    self._sides = [ [] for i in range(6) ]

  def move(self, pos):
    """Move the object to a new position."""
    self._pos = pos

  def onActorCollide(self, actor):
    """Perform actions when an Actor hits this object."""
    actor.health += _dHealth
    # TODO: block the actor if _blocking is True

  def draw(self):
    """Render the object to the OpenGL display."""
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER, 0.5)

    glEnable(GL_TEXTURE_2D)
    self._spritesheet.bindTexture()
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBegin(GL_QUADS)
    glColor4f(1, 1, 1, 1)
    for plane, side in enumerate(self._sides):
      if plane == 0 or plane == 1: # XXX xy (front)
        v = [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
      elif plane == 2 or plane == 3: # XXX xz (bottom)
        v = [(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)]
      elif plane == 4 or plane == 5: # XXX yz (left)
        v = [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]
      
      x = self._pos[0]
      y = self._pos[1]
      z = 0

      if len(self._sides[plane]) == 0: continue
      tile = self._sides[plane]

      self._spritesheet.tileCoord(tile, 0, 0)
      glVertex3f(x + v[0][0], y + v[0][1], z + v[0][2])

      self._spritesheet.tileCoord(tile, 1, 0)
      glVertex3f(x + v[1][0], y + v[1][1], z + v[1][2])

      self._spritesheet.tileCoord(tile, 1, 1)
      glVertex3f(x + v[2][0], y + v[2][1], z + v[2][2])

      self._spritesheet.tileCoord(tile, 0, 1)
      glVertex3f(x + v[3][0], y + v[3][1], z + v[3][2])
    glEnd()

class Back(LevelObject):
  """The blocks in the background"""

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)
    
    self._sides[1].append("wall.png")

class BackAboveFloor(LevelObject):
  """The background above a Floor tile"""

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[1].append("wall-floor.png")

class Transport(LevelObject):
  """An object that can move Actors"""

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[1].append("portal.png")

class Start(Transport):
  """The Player's spawn point"""

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[1].append("start.png")

class Ladder(Transport):
  """A ladder"""

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[1].append("ladder.png")

class LadderOnFloor(Transport):
  """A ladder"""

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[1].append("ladder-floor.png")

class Door(Transport):
  """A door, which is usually the level's goal"""

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[1].append("door.png")

class Barrier(LevelObject):
  """A barrier that blocks the player"""

  _blocking = True

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[0].append("floor-top.png")
    self._sides[1].append("floor-top.png")
    self._sides[2].append("floor-top.png")
    self._sides[3].append("floor-top.png")
    self._sides[4].append("floor-top.png")
    self._sides[5].append("floor-top.png")

class Wall(Barrier):
  """A vertical wall that blocks horizontal movement"""

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[0].append("wall-floor.png")
    self._sides[2].append("floor-top.png")
    self._sides[3].append("floor-top.png")
    self._sides[4].append("wall-floor.png")
    self._sides[5].append("wall-floor.png")

class Floor(Barrier):
  """A horizontal surface that blocks vertical movement"""

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[0].append("floor-front.png")
    self._sides[1].append("wall.png")
    self._sides[2].append("floor-top.png")
    self._sides[4].append("floor-side.png")
    self._sides[5].append("floor-side.png")

class Actor(LevelObject):
  """The player and enemies"""

  _blocking = True
  _walkSpeed = 1
  _jumpSpeed = 1
  health = 100  
  maxHealth = 100

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[0].append("skeleton.png")

  def draw(self):
    # TODO: implement!
    pass

class Player(Actor):
  """The player"""

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[0].append("robot0.png")
    self._sides[0].append("robot1.png")
    self._sides[0].append("robot2.png")
    self._sides[0].append("robot3.png")

# TODO: more objects

NAMES = {
  "object" : LevelObject,
  "back" : Back,
  "backF" : BackAboveFloor,
  "transport" : Transport,
  "start" : Start,
  "ladder" : Ladder,
  "ladderF" : LadderOnFloor,
  "door" : Door,
  "barrier" : Barrier,
  "wall" : Wall,
  "floor" : Floor,
  # "fire" : Fire,
  # "actor" : Actor,
  # "player" : Player,
}
