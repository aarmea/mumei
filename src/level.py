import pygame

class Level(object):
  """A level"""

  def __init__(self, ui):
    self.__ui = ui

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
    """Draw the level interface."""
    self.__ui.drawBackground(0, 1, 0)