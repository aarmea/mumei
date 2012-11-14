#!/usr/bin/env python

from OpenGL.GL import *
import pygame

from level import Level
from texture import Texture

class UI(object):
  """The main user interface object"""

  def __init__(self):
    pygame.init()

    self.screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Mumei")
    pygame.mouse.set_visible(False)

    # Set up the projection matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-640 / 64 / 2, 640 / 64 / 2, -480 / 64 / 2, 480 / 64 / 2, -10, 10)

    # Set up the initial state
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
    quit = False
    clock = pygame.time.Clock()
    time = 0.0

    while len(self.stateStack) and not quit:
      currentState = self.stateStack[-1]
      quit = currentState.handleEvents(pygame.event.get())
      time += clock.tick()
      currentState.draw(time)
      pygame.display.flip()

class Menu(object):
  """The base class for all menus"""

  def __init__(self, ui):
    self._ui = ui

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

  def userUp(self):
    """The default up handler"""

  def userDown(self):
    """The default down handler"""

  def userSelect(self):
    """The default select handler"""

  def userBack(self):
    """The default back handler"""
    self._ui.popState()

class PlainMenu(Menu):
  """A menu with a single textured quad"""

  def __init__(self, ui, textureFile):
    super(PlainMenu, self).__init__(ui)
    self.__texture = Texture(textureFile)

  def draw(self, time):
    """Draw the menu."""
    # Clear the screen
    glClearColor(0, 0, 1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Reset the modelview matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Draw the menu quad
    self.__texture.bind()
    glBegin(GL_QUADS);
    if True:
      glTexCoord2d(0.0, 0.0); glVertex2d(-5.0,-4.0);
      glTexCoord2d(1.0, 0.0); glVertex2d( 5.0,-4.0);
      glTexCoord2d(1.0, 1.0); glVertex2d( 5.0, 3.0);
      glTexCoord2d(0.0, 1.0); glVertex2d(-5.0, 3.0);
    glEnd();

class MainMenu(PlainMenu):
  """The main menu"""

  def __init__(self, ui):
    super(MainMenu, self).__init__(ui, "../assets/background.png")

  def userSelect(self):
    self._ui.pushState(LevelMenu(self._ui))

class LevelMenu(PlainMenu):
  """The level menu"""

  def __init__(self, ui):
    super(LevelMenu, self).__init__(ui, "../assets/background2.png")

  def userSelect(self):
    self._ui.pushState(Level(self._ui, "level00.csv"))

def main():
  """Create and run the UI."""
  ui = UI()
  ui.run()

if __name__ == "__main__":
  main()
