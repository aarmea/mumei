import sys

import pygame

class Screen(object):
  """The base class for all screens"""

  def __init__(self, ui):
    self._ui = ui

  def closeScreen(self):
    self._ui.popState()

  def handleEvents(self, events):
    for e in events:
      if e.type == pygame.QUIT:
        sys.exit()

  def update(self, time):
    pass

  def draw(self):
    raise NotImplementedError("draw")
