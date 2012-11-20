import sys

import pygame

from screen import Screen

class Menu(Screen):
  """A base class for menus that provides an event handler that dispatches to
  functions provided by derived classes (userUp(), userDown(), userSelect(),
  userBack())"""

  def handleEvents(self, events):
    """Handle user input events"""
    super(Menu, self).handleEvents(events)

    for e in events:
      if e.type == pygame.KEYDOWN:
        if e.key == pygame.K_UP:
          self.userUp()
        elif e.key == pygame.K_DOWN:
          self.userDown()
        elif e.key == pygame.K_RETURN:
          self.userSelect()
        elif e.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
          self.userBack()
        if e.key == pygame.K_q:
          sys.exit()

  def userUp(self):
    """The default up handler"""

  def userDown(self):
    """The default down handler"""

  def userSelect(self):
    """The default select handler"""

  def userBack(self):
    """The default back handler"""
    self.closeScreen()
