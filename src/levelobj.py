import csv
import math

from OpenGL.GL import *
import pygame

import vm.bytecode

from textureatlas import *

COLORS = {
  0 : "",
  1 : "R",
  2 : "G",
  3 : "B"
}

# Direction values
DIRECTION_NONE = 0
DIRECTION_LEFT = 1
DIRECTION_RIGHT = 2
DIRECTION_DOWN = 3
DIRECTION_UP = 4

EPSILON = 0.01

def withinEpsilon(x):
  return abs(x) < EPSILON

class LevelObject(object):
  """An object within a level"""

  blocking = False
  _sides = ["default.png"] * 6

  def __init__(self, pos, spritesheet, level):
    self._pos = pos
    self._spritesheet = spritesheet
    self._level = level

  def draw(self):
    """Render the object"""
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

      if len(self._sides[plane]) == 0:
        continue

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

  _sides = [
    [],
    ["wall.png"],
    [],
    [],
    [],
    []
  ]

class BackAboveFloor(LevelObject):
  """The background above a Floor tile"""

  _sides = [
    [],
    ["wall-floor.png"],
    [],
    [],
    [],
    [],
    []
  ]

class Transport(LevelObject):
  """An object that can move Actors"""

  _sides = [
    [],
    ["portal.png"],
    [],
    [],
    [],
    []
  ]

class Start(Transport):
  """The Player's spawn point"""

  _sides = [
    [],
    ["start.png"],
    [],
    [],
    [],
    []
  ]

class Ladder(Transport):
  """A ladder"""

class LadderLeft(Ladder):
  """A ladder"""

  _sides = [
    [],
    ["wall.png"],
    [],
    [],
    ["ladder.png"],
    []
  ]

class LadderLeftFloor(Ladder):
  """A ladder"""

  _sides = [
    [],
    ["wall-floor.png"],
    [],
    [],
    ["ladder.png"],
    []
  ]

class LadderRight(Ladder):
  """A ladder"""

  _sides = [
    [],
    ["wall.png"],
    [],
    [],
    [],
    ["ladder.png"]
  ]

class LadderRightFloor(Ladder):
  """A ladder"""

  _sides = [
    [],
    ["wall-floor.png"],
    [],
    [],
    [],
    ["ladder.png"]
  ]

class LadderOnFloor(Ladder):
  """A ladder"""

  _sides = [
    [],
    ["wall.png"],
    [],
    [],
    ["ladder-floor.png"],
    [],
  ]

class Door(Transport):
  """A door, which is usually the level's goal"""

  def __init__(self, pos, spritesheet, level, color=0):
    Transport.__init__(self, pos, spritesheet, level)
    self.color = color

  def __getColor(self):
    return self.__color

  def __setColor(self, color):
    self.__color = color

    # Change the sprites to those with the given color
    colorStr = COLORS[color]
    self._sides = [
      [],
      ["door%s.png" % colorStr],
      [],
      [],
      [],
      []
    ]

  color = property(__getColor, __setColor)

class Barrier(LevelObject):
  """A barrier that blocks the player"""

  blocking = True
  _sides = ["floor-top.png"] * 6

class Skeleton(Barrier):
  """RAWR"""

  _sides = [
    [],
    ["wall-floor.png"],
    [],
    [],
    ["skeleton.png"]
  ]

class Pickle(Barrier):
  """RAWR"""

  _sides = [
    ["pickle.png"],
    ["wall-floor.png"],
    ["pickle.png"],
    ["pickle.png"],
    ["pickle.png"],
    ["pickle.png"]
  ]

class Wall(Barrier):
  """A vertical wall that blocks horizontal movement"""

  _sides = [
    ["wall.png"],
    [],
    ["floor-top.png"],
    ["floor-top.png"],
    ["wall.png"],
    ["wall.png"],
    ["wall.png"]
  ]

class Floor(Barrier):
  """A horizontal surface that blocks vertical movement"""

  _sides = [
    ["floor-front.png"],
    ["wall.png"],
    ["floor-top.png"],
    [],
    ["floor-side.png"],
    ["floor-side.png"]
  ]

class Actor(LevelObject):
  """The player and enemies"""

  blocking = True
  _speed = 5

  _sides = [
    ["skeleton.png"],
    [],
    [],
    [],
    [],
    []
  ]

  def __init__(self, ui, level, pos):
    LevelObject.__init__(self, pos, ui.spritesheet, level)
    self.direction = DIRECTION_NONE

  def step(self):
    stepSize = self._speed * 10.0 / 1000

    if self.direction == DIRECTION_LEFT:
      newPos = (self._pos[0] - stepSize, self._pos[1])
    elif self.direction == DIRECTION_RIGHT:
      newPos = (self._pos[0] + stepSize, self._pos[1])
    elif self.direction == DIRECTION_DOWN:
      newPos = (self._pos[0], self._pos[1] - stepSize)
    elif self.direction == DIRECTION_UP:
      newPos = (self._pos[0], self._pos[1] + stepSize)
    else:
      newPos = self._pos

    obj1 = self._level.at((int(newPos[0] + EPSILON), int(newPos[1] + EPSILON)))
    obj2 = self._level.at((int(newPos[0] + 1 + EPSILON), int(newPos[1] + EPSILON)))

    if not obj1.blocking and not obj2.blocking:
      self._pos = newPos

    # Gravity
    obj1 = self._level.at((int(self._pos[0] + EPSILON), int(self._pos[1] + EPSILON)))
    obj2 = self._level.at((int(self._pos[0] + EPSILON), int(self._pos[1] - EPSILON)))

    if not isinstance(obj1, Ladder) and not obj2.blocking:
      self._pos = (self._pos[0], self._pos[1] - stepSize)

class Robot(Actor):
  """The robot"""

  _speed = 2;

  class ControlRegister(object):
    """A memory-mapped control register with a descriptor interface."""

    def __init__(self, label):
      self.label = label

    def __get__(self, instance, owner):
      try:
        addr = instance._labels[self.label]
        return instance._processor.getMem(addr)
      except AttributeError:
        return None

    def __set__(self, instance, value):
      try:
        addr = instance._labels[self.label]
        return instance._processor.setMem(addr, value)
      except AttributeError:
        pass

  def __init__(self, ui, level, pos):
    self._processor = None
    Actor.__init__(self, ui, level, pos)

  def load(self, words, labels):
    # Create a new processor
    processor = vm.bytecode.Processor(memWords=0x1000)

    # Load the bytecode into memory
    for addr, word in enumerate(words):
      processor.setMem(addr, word)

    # Store the label addresses
    self._labels = labels

    # Set IP to the entry point
    entry = labels["main"]
    processor.setReg(processor.REG_IP, entry)

    self._processor = processor

    # Initialize the control registers
    self.direction = DIRECTION_NONE
    self.color = 0

  def step(self):
    """Update the robot's state"""
    if self._processor is not None:
      # Run the processor at 20x the step rate
      for _ in xrange(20):
        self._processor.step()

      self.x = int(self._pos[0])
      self.y = int(self._pos[1])

    # Change the sprites to those with the given color
    try:
      colorStr = COLORS[self.color]
    except KeyError:
      colorStr = "" # XXX Should probably use a default dictionary

    self._sides = [
      ["robot0%s.png" % colorStr, "robot1%s.png" % colorStr,
       "robot2%s.png" % colorStr, "robot2%s.png" % colorStr],
      [],
      [],
      [],
      [],
      []
    ]

    Actor.step(self)

  # Memory-mapped control registers
  x = ControlRegister("x")
  y = ControlRegister("y")
  direction = ControlRegister("dir")
  color = ControlRegister("color")

class Player(Actor):
  """The player"""

  _sides = [
    ["person.png"],
    [],
    [],
    [],
    [],
    []
  ]

# TODO: more objects

NAMES = {
  "object" : LevelObject,
  "back" : Back,
  "backF" : BackAboveFloor,
  "transport" : Transport,
  "start" : Start,
  "ladder" : Ladder,
  "ladderF" : LadderOnFloor,
  "ladderL" : LadderLeft,
  "ladderLF" : LadderLeftFloor,
  "ladderR" : LadderRight,
  "ladderRF" : LadderRightFloor,
  "door" : Door,
  "doorR" : lambda pos, spritesheet, level: Door(pos, spritesheet, level, 1),
  "doorG" : lambda pos, spritesheet, level: Door(pos, spritesheet, level, 2),
  "barrier" : Barrier,
  "wall" : Wall,
  "skeleton" : Skeleton,
  "floor" : Floor,
  "pickle" :Pickle,
  # "fire" : Fire,
  # "actor" : Actor,
  # "player" : Player,
}
