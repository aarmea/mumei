from OpenGL.GL import *
import pygame

# TODO: implement the sprite atlas at "assets/spritesheet-0.png"
spriteDir = "../assets/sprites/"

class LevelObject(object):
  """The base level object"""

  _dHealth = 0
  _blocking = False

  _front = []
  _back = []
  _top = []
  _bottom = []
  _left = []
  _right = []

  def __init__(self, pos):
    self._pos = pos

    self._front.append(pygame.image.load(spriteDir + "default.png").convert_alpha())

  def move(self, pos):
    """Move the object to a new position."""
    self._pos = pos

  def onActorCollide(self, actor):
    """Perform actions when an Actor hits this object."""
    actor.health += _dHealth
    # TODO: block the actor if _blocking is True

  def render(self):
    """Render the object to the OpenGL display."""
    # TODO: implement!
    pass

class Back(LevelObject):
  """The blocks in the background"""

  def __init__(self, pos):
    self._pos = pos
    
    self._back.append(pygame.image.load(spriteDir + "wall.png").convert_alpha())

class BackAboveFloor(LevelObject):
  """The background above a Floor tile"""

  def __init__(self, pos):
    self._pos = pos

    self._back.append(pygame.image.load(spriteDir + "wall-floor.png").convert_alpha())

class Transport(LevelObject):
  """An object that can move Actors"""

  def __init__(self, pos):
    self._pos = pos

    self._back.append(pygame.image.load(spriteDir + "portal.png").convert_alpha())

class Start(Transport):
  """The Player's spawn point"""

  def __init__(self, pos):
    self._pos = pos

    self._back.append(pygame.image.load(spriteDir + "start.png").convert_alpha())

class Ladder(Transport):
  """A ladder"""

  def __init__(self, pos):
    self._pos = pos

    self._back.append(pygame.image.load(spriteDir + "ladder.png").convert_alpha())

class LadderOnFloor(Transport):
  """A ladder"""

  def __init__(self, pos):
    self._pos = pos

    self._back.append(pygame.image.load(spriteDir + "ladder-floor.png").convert_alpha())

class Door(Transport):
  """A door, which is usually the level's goal"""

  def __init__(self, pos):
    self._pos = pos

    self._back.append(pygame.image.load(spriteDir + "door.png").convert_alpha())

class Barrier(LevelObject):
  """A barrier that blocks the player"""

  _blocking = True

  def __init__(self, pos):
    self._pos = pos

    self._front.append(pygame.image.load(spriteDir + "floor-top.png").convert_alpha())
    self._back.append(pygame.image.load(spriteDir + "floor-top.png").convert_alpha())
    self._top.append(pygame.image.load(spriteDir + "floor-top.png").convert_alpha())
    self._bottom.append(pygame.image.load(spriteDir + "floor-top.png").convert_alpha())
    self._left.append(pygame.image.load(spriteDir + "floor-top.png").convert_alpha())
    self._right.append(pygame.image.load(spriteDir + "floor-top.png").convert_alpha())

class Wall(Barrier):
  """A vertical wall that blocks horizontal movement"""

  def __init__(self, pos):
    self._pos = pos

    self._front.append(pygame.image.load(spriteDir + "wall-floor.png").convert_alpha())
    self._top.append(pygame.image.load(spriteDir + "floor-top.png").convert_alpha())
    self._bottom.append(pygame.image.load(spriteDir + "floor-top.png").convert_alpha())
    self._left.append(pygame.image.load(spriteDir + "wall-floor.png").convert_alpha())
    self._right.append(pygame.image.load(spriteDir + "wall-floor.png").convert_alpha())

class Floor(Barrier):
  """A horizontal surface that blocks vertical movement"""

  def __init__(self, pos):
    self._pos = pos

    self._front.append(pygame.image.load(spriteDir + "floor-front.png").convert_alpha())
    self._back.append(pygame.image.load(spriteDir + "wall.png").convert_alpha())
    self._top.append(pygame.image.load(spriteDir + "floor-top.png").convert_alpha())
    self._left.append(pygame.image.load(spriteDir + "floor-side.png").convert_alpha())
    self._right.append(pygame.image.load(spriteDir + "floor-side.png").convert_alpha())

class Actor(LevelObject):
  """The player and enemies"""

  _blocking = True
  _walkSpeed = 1
  _jumpSpeed = 1
  health = 100  
  maxHealth = 100

  def __init__(self, pos):
    self._pos = pos

    self._front.append(pygame.image.load(spriteDir + "skeleton.png"))

  def render(self):
    # TODO: implement!
    pass

class Player(Actor):
  """The player"""

  def __init__(self, pos):
    self._pos = pos

    self._front.append(pygame.image.load(spriteDir + "robot0.png"))
    self._front.append(pygame.image.load(spriteDir + "robot1.png"))
    self._front.append(pygame.image.load(spriteDir + "robot2.png"))
    self._front.append(pygame.image.load(spriteDir + "robot3.png"))

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
