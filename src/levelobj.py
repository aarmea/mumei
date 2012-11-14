import csv
import math

from OpenGL.GL import *
import pygame

from texture import Texture

EPSILON = 0.01

class TileSet(object):
  """An interface for texturing quads with tiles from a single texture"""

  def __init__(self, path, prefix):
    # TODO: handle multiple spritesheets

    # Parse the *.csv file
    self.__images = dict()
    with open(path + prefix + ".csv") as file_:
      csvFile = csv.reader(file_)

      for meta in csvFile:
        # Parse each individual element
        # Format: __images[sprite name] = (sheet file, top left corner, size)
        self.__images[meta[0]] = (meta[1], (int(meta[2]), int(meta[3])),
          (int(meta[4]), int(meta[5])))

      file_.close()

    # Load the texture
    self.__texture = Texture(path + prefix + "-0.png")

    # Pick a sprite and assume all the other sprites are the same size
    self.__tilew, self.__tileh = self.__images.values()[0][2]

    # Calculate placement parameters
    self.__es = 1.0 / self.__texture.w
    self.__et = 1.0 / self.__texture.h
    self.__htiles = self.__texture.w / self.__tilew
    self.__vtiles = self.__texture.h / self.__tileh
    self.__ntiles = self.__htiles * self.__vtiles

  def bind(self):
    """Bind this tile set."""
    self.__texture.bind()

  def tileCoord(self, spriteName, u, v):
    """Set the texture coordinates for the given tile."""
    s = self.__images[spriteName][1][0] / self.__tilew
    t = self.__images[spriteName][1][1] / self.__tileh
    assert s < self.__htiles
    assert t < self.__vtiles
    assert u >= 0.0 and u <= 1.0
    assert v >= 0.0 and v <= 1.0
    glTexCoord2f((s + u) * self.__tilew * self.__es,
      (self.__texture.h - (t + 1.0 - v) * self.__tileh) * self.__et)

class LevelObject(object):
  """The base level object"""

  _dHealth = 0
  _blocking = False

  _moving = False
  _moveStep = (1.0, 1.0)
  _dest = (0, 0)

  def __init__(self, pos, spritesheet):
    self._uinit(pos, spritesheet)

    self._sides[0].append("default.png")

  def _uinit(self, pos, spritesheet):
    """Initialization common to all child classes."""
    self._pos = (float(pos[0]), float(pos[1]))
    self._spritesheet = spritesheet
    # Format: 0 = front, 1 = back, 2 = top, 3 = bottom, 4 = left, 5 = right
    self._sides = [ [] for i in range(6) ]

  def move(self, pos):
    """Move the object to a new position."""
    self._pos = (float(pos[0]), float(pos[1]))

  def relMove(self, pos):
    """Move the object to a new position relative to it's current location."""
    # self._pos = (self._pos[0] + pos[0], self._pos[1], + pos[1])
    if not self._moving:
      self._dest = (self._pos[0] + pos[0], self._pos[1], + pos[1])
      self._moveStep = (float(self._dest[0] - self._pos[0]) / 16, 
                        float(self._dest[1] - self._pos[1]) / 16)
      self._moving = True

  def onActorCollide(self, actor):
    """Perform actions when an Actor hits this object."""
    actor.health += _dHealth
    # TODO: block the actor if _blocking is True

  def draw(self):
    """Render the object to the OpenGL display."""
    # Move the object for animated relative moves
    if self._moving:
      # Stop moving if it's at or near the destination
      if abs(self._dest[0]-self._pos[0]) < EPSILON and \
         abs(self._dest[1]-self._pos[1]) < EPSILON:
        self._moving = False
        self._pos = self._dest
      else:
        # Move the object by _moveStep
        self._pos = (self._pos[0] + self._moveStep[0],
                     self._pos[1] + self._moveStep[1])

    # Draw stuff
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER, 0.5)

    glEnable(GL_TEXTURE_2D)
    self._spritesheet.bind()
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBegin(GL_QUADS)
    glColor4f(1, 1, 1, 1)
    for plane, side in enumerate(self._sides):
      if plane == 0: # XXX xy (front)
        v = [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
      elif plane == 1: # back
        v = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
      elif plane == 2: # XXX xz (bottom)
        v = [(0, 1, 1), (1, 1, 1), (1, 1, 0), (0, 1, 0)]
      elif plane == 3: # top
        v = [(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)]
      elif plane == 4: # XXX yz (left)
        v = [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]
      elif plane == 5: # right
        v = [(1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)]
      
      x = self._pos[0]
      y = self._pos[1]
      z = 0

      if len(self._sides[plane]) == 0: continue
      tile = self._sides[plane][0]

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

    self._sides[0].append("wall.png")
    self._sides[2].append("floor-top.png")
    self._sides[3].append("floor-top.png")
    self._sides[4].append("wall.png")
    self._sides[5].append("wall.png")

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
