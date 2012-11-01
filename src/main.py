#!/usr/bin/env python

from OpenGL.GL import *
# from OpenGL.GLU import * # for perspective
import pygame

from level import Level



class UI(object):
  """The main user interface object"""

  def __init__(self):
    pygame.init()

    self.screen = pygame.display.set_mode((800, 600), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Mumei")
    pygame.mouse.set_visible(False)
    # XXX pygame.key.set_repeat(10, 10)

    # Set up OpenGL
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-640 / 64 / 2, 640 / 64 / 2, -480 / 64 / 2, 480 / 64 / 2, -10, 10)
    # For perspective stuff, comment the line above and uncomment the line below
    # gluPerspective(90, 0.75, 1, 10)

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
    self.__surface = pygame.image.load("background.png").convert_alpha()
    self.__tex = glGenTextures(1)
    glEnable(GL_TEXTURE_2D);
    glBindTexture(GL_TEXTURE_2D,self.__tex);
    self.__w, self.__h = self.__surface.get_size()
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.__w, self.__h, 0, GL_RGBA,
      GL_UNSIGNED_BYTE, pygame.image.tostring(self.__surface, "RGBA", True))

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
    glClearColor(0, 0, 1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glBindTexture(GL_TEXTURE_2D,self.__tex);
    glBegin( GL_QUADS );
    glTexCoord2d(0.0,0.0); glVertex2d(-5.0,-4.0);
    glTexCoord2d(1.0,0.0); glVertex2d(5.0,-4.0);
    glTexCoord2d(1.0,1.0); glVertex2d(5.0,3.0);
    glTexCoord2d(0.0,1.0); glVertex2d(-5.0,3.0);
    glEnd();


class LevelMenu(Menu):
  """The level menu"""

  def __init__(self, ui):
    self.__ui = ui
    self.__surface = pygame.image.load("background2.png").convert_alpha()
    self.__tex = glGenTextures(1)
    glEnable(GL_TEXTURE_2D);
    glBindTexture(GL_TEXTURE_2D,self.__tex);
    self.__w, self.__h = self.__surface.get_size()
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.__w, self.__h, 0, GL_RGBA,
    GL_UNSIGNED_BYTE, pygame.image.tostring(self.__surface, "RGBA", True))

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
    glClearColor(0, 0, 1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glBindTexture(GL_TEXTURE_2D,self.__tex);
    glBegin( GL_QUADS );
    glTexCoord2d(0.0,0.0); glVertex2d(-5.0,-4.0);
    glTexCoord2d(1.0,0.0); glVertex2d(5.0,-4.0);
    glTexCoord2d(1.0,1.0); glVertex2d(5.0,3.0);
    glTexCoord2d(0.0,1.0); glVertex2d(-5.0,3.0);
    glEnd();

def main():
  ui = UI()
  ui.run()

if __name__ == "__main__":
  main()
