#!/usr/bin/env python

from OpenGL.GL import *
import pygame

from level import Level

class UI(object):
  """The main user interface object"""

  def __init__(self):
    pygame.init()

    pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Mumei")
    pygame.mouse.set_visible(False)
    # XXX pygame.key.set_repeat(10, 10)

    # Set up OpenGL
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-640 / 64 / 2, 640 / 64 / 2, -480 / 64 / 2, 480 / 64 / 2, -10, 10)

    self.stateStack = [MainMenu(self)]

  def pushState(self, state):
    """Add a state to the state stack. The new state will become the active
    state."""
    self.stateStack.append(state)

  def popState(self):
    """Remove a state from the state stack. The previous state will become the
    active state."""
    self.stateStack.pop()

  def drawBackground(self, r, g, b):
    """Fill the background with the given color."""
    glClearColor(r, g, b, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

  def run(self):
    """Run the main UI loop."""
    while len(self.stateStack):
      currentState = self.stateStack[-1]
      quit = currentState.handleEvents(pygame.event.get())
      currentState.draw()
      pygame.display.flip()
      if quit: break

class Menu(object):
  """The base menu class"""
  
  def __init__(self, ui):
    self.__ui = ui

  def handleEvents(self, events):
    """Handle keyboard input. Returns True if the game should quit."""
    for e in events:
      if e.type == pygame.QUIT:
        return True
      elif e.type == pygame.KEYDOWN:
        if e.key == pygame.K_UP:
          self.userUp()
        elif e.key == pygame.K_DOWN:
          self.userDown()

        elif e.key == pygame.K_RETURN:
          self.userSelect()
        elif e.key == pygame.K_ESCAPE:
          self.userBack()

        elif e.key == pygame.K_q:
          return True
    return False

class MainMenu(Menu):
  """The main menu"""

  def __init__(self, ui):
    self.__ui = ui

  def userUp(self):
    print "Main: user up"

  def userDown(self):
    print "Main: user down"

  def userSelect(self):
    print "Main: user select"
    self.__ui.pushState(LevelMenu(self.__ui))

  def userBack(self):
    print "Main: user back"
    self.__ui.popState()

  def draw(self):
    """Draw the user interface."""
    self.__ui.drawBackground(0, 0, 1)

class LevelMenu(Menu):
  """The level menu"""

  def __init__(self, ui):
    self.__ui = ui

  def userUp(self):
    print "LevelMenu: user up"

  def userDown(self):
    print "LevelMenu: user down"

  def userSelect(self):
    print "LevelMenu: user select"
    self.__ui.pushState(Level(self.__ui, "level00.csv"))

  def userBack(self):
    print "LevelMenu: user back"
    self.__ui.popState()

  def draw(self):
    """Draw the user interface."""
    self.__ui.drawBackground(1, 0, 0)

def main():
  ui = UI()
  ui.run()

if __name__ == "__main__":
  main()
