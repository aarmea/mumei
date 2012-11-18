#!/usr/bin/env python

import threading
import os

from OpenGL.GL import *
import pygame

from level import Level
from texture import Texture
from textureatlas import TileSet

class UI(object):
  """The main user interface object"""

  def __init__(self):
    pygame.init()
    pygame.key.set_repeat(250, 50)

    self.screen = pygame.display.set_mode((1024, 768), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("Mumei")
    pygame.mouse.set_visible(False)

    # Set up the projection matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1024 / 64 / 2, 1024 / 64 / 2, -768 / 64 / 2, 768 / 64 / 2, -10, 10)

    # Load the tile set
    self.spritesheet = TileSet("../assets/", "spritesheet")

    # Set up the initial player state
    self.hair = 0
    self.head = 0
    self.shirt = 0
    self.pants = 0

    # Set up the initial screen state
    self.stateStack = [WelcomeScreen(self)]

  def pushState(self, state):
    """Add a state to the state stack. The new state will become the active
    state."""
    self.stateStack.append(state)

  def popState(self):
    """Remove a state from the state stack. The previous state will become the
    active state."""
    self.stateStack.pop()

  #def drawBackground(self, r, g, b):
  #  """Fill the background with the given color."""
  #  glClearColor(r, g, b, 1)
  #  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Reset the modelview matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Draw the menu quad
    glEnable(GL_TEXTURE_2D)
    self.__texture.bind()
    glBegin(GL_QUADS);
    if True:
      glTexCoord2d(0.0, 0.0); glVertex2d(-5.0,-4.0);
      glTexCoord2d(1.0, 0.0); glVertex2d( 5.0,-4.0);
      glTexCoord2d(1.0, 1.0); glVertex2d( 5.0, 3.0);
      glTexCoord2d(0.0, 1.0); glVertex2d(-5.0, 3.0);
    glEnd();

class CharacterSelectMenu(PlainMenu):
  """A screen that allows the user to select their character's appearance"""

  NHAIRS = 3
  NHEADS = 2
  NSHIRTS = 2
  NPANTS = 2

  def __init__(self, ui):
    PlainMenu.__init__(self, ui, "../assets/charactermenu.png")

  def rebuildPlayer(self):
    """Recreate the player sprite and reload the sprite sheet."""
    playerSub = self._ui.spritesheet.subsurface("person.png")
    hairSub = self._ui.spritesheet.subsurface(
      "hair%d.png" % self._ui.hair).copy()
    headSub = self._ui.spritesheet.subsurface(
      "head%d.png" % self._ui.head).copy()
    shirtSub = self._ui.spritesheet.subsurface(
      "shirt%d.png" % self._ui.shirt).copy()
    pantsSub = self._ui.spritesheet.subsurface(
      "pants%d.png" % self._ui.pants).copy()

    playerSub.fill((0, 0, 0, 0))
    playerSub.blit(pantsSub, (0, 0))
    playerSub.blit(headSub, (0, 0))
    playerSub.blit(shirtSub, (0, 0))
    playerSub.blit(hairSub, (0, 0))

    self._ui.spritesheet.reload()

  def handleEvents(self, events):
    for e in events:
      if e.type == pygame.KEYDOWN:
        if e.key == pygame.K_w:
          self._ui.hair = (self._ui.hair - 1) % self.NHAIRS
          self.rebuildPlayer()
        elif e.key == pygame.K_s:
          self._ui.hair = (self._ui.hair + 1) % self.NHAIRS
          self.rebuildPlayer()

        elif e.key == pygame.K_e:
          self._ui.head = (self._ui.head - 1) % self.NHEADS
          self.rebuildPlayer()
        elif e.key == pygame.K_d:
          self._ui.head = (self._ui.head + 1) % self.NHEADS
          self.rebuildPlayer()

        elif e.key == pygame.K_r:
          self._ui.shirt = (self._ui.shirt - 1) % self.NSHIRTS
          self.rebuildPlayer()
        elif e.key == pygame.K_f:
          self._ui.shirt = (self._ui.shirt + 1) % self.NSHIRTS
          self.rebuildPlayer()

        elif e.key == pygame.K_t:
          self._ui.pants = (self._ui.pants - 1) % self.NPANTS
          self.rebuildPlayer()
        elif e.key == pygame.K_g:
          self._ui.pants = (self._ui.pants + 1) % self.NPANTS
          self.rebuildPlayer()

    return super(CharacterSelectMenu, self).handleEvents(events)

  def userSelect(self):
    self._ui.pushState(LevelMenu(self._ui))

  def draw(self, time):
    """Draw the background image"""
    PlainMenu.draw(self, time)

    glEnable(GL_ALPHA_TEST)
    glAlphaFunc(GL_GREATER, 0.5)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glEnable(GL_DEPTH_TEST)

    glEnable(GL_TEXTURE_2D)
    self._ui.spritesheet.bind()
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_COMBINE)

    glBegin(GL_QUADS)
    if True:
      # Draw the sprite
      self._ui.spritesheet.tileCoord("person.png", 0, 0)
      glVertex3f(-2, -2.5, 1)

      self._ui.spritesheet.tileCoord("person.png", 1, 0)
      glVertex3f(2, -2.5, 1)

      self._ui.spritesheet.tileCoord("person.png", 1, 1)
      glVertex3f(2, 1.5, 1)

      self._ui.spritesheet.tileCoord("person.png", 0, 1)
      glVertex3f(-2, 1.5, 1)

    glEnd()

class WelcomeScreen(PlainMenu):
  """The welcome screen - splash"""

  def __init__(self, ui):
    super(WelcomeScreen, self).__init__(ui, "../assets/background.png")

  def userSelect(self):
    self._ui.pushState(CharacterSelectMenu(self._ui))

class LevelButton(object):
  """Faux button that indicates available level choices"""
  def __init__(self, ui, imgfile):
    self._ui = ui
    self.__texture = Texture(imgfile)

class LevelMenu(PlainMenu):
  """The main level menu - interactable"""

  def __init__(self, ui):
    super(LevelMenu, self).__init__(ui, "../assets/levelmenu.png")
    # contains a series of level buttons
    level1button = LevelButton(ui, "../assets/level1mockbutton.png")

  def handleEvents(self, events):
    """Handle keyboard input for level selection. Returns True if the game should quit."""
    MasterLevelDictonary = [ ["level100", "level101", "level102", "level103", "level104"],
                             ["level200", "level201", "level202", "level203", "level204"],
                             ["level300", "level301", "level302", "level303", "level304"] ]
    for e in events:
      if e.type == pygame.QUIT:
        return True
      elif e.type == pygame.KEYDOWN:
        if e.key == pygame.K_UP:
          self.userUp()
        elif e.key == pygame.K_DOWN:
          self.userDown()
        #elif e.key == pygame.K_RETURN:
        #  self.userSelect()
        elif e.key == pygame.K_ESCAPE:
          self.userBack()
        elif e.key == pygame.K_1:
          self.userSelectLevel(MasterLevelDictonary[0][2])
        elif e.key == pygame.K_2:
          self.userSelectLevel(MasterLevelDictonary[1][0])
        elif e.key == pygame.K_3:
          self.userSelectLevel(MasterLevelDictonary[2][0])
        elif e.key == pygame.K_q:
          return True
    return False

  def userSelectLevel(self, basename):
    self._ui.pushState(LevelScreen(self._ui, basename)) # push the state for that level splash screen

class LevelScreen(PlainMenu):
  """The level screen - splash"""

  def __init__(self, ui, basename):
    super(LevelScreen, self).__init__(ui, "../assets/background2.png")
    self.basename = basename

  def userSelect(self):
    self._ui.pushState(Level(self._ui, self.basename))

def main():
  """Create and run the UI."""
  ui = UI()
  ui.run()

if __name__ == "__main__":
  print "Mumei running on", os.name
  if os.name == "nt":
    print "Increasing the stack size to 64MB..."
    # Windows 64 fix, see http://stackoverflow.com/questions/2917210/
    threading.stack_size(67108864)
    thread = threading.Thread(target=main)
    thread.start()
  else:
    main()
