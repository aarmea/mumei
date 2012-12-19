#!/usr/bin/env python

import os
import sys
import threading

from OpenGL.GL import *
import pygame

from characterselect import CharacterSelectScreen
from menu import Menu
from levelscreen import LevelScreen
from screen import SimpleScreen
from ui import UI

class WelcomeScreen(SimpleScreen):
  """The welcome screen - splash"""

  def __init__(self, ui):
    super(WelcomeScreen, self).__init__(ui, "assets/welcometomumei.png")

  def handleEvents(self, events):
    """Handle user input events"""
    for e in events:
      if e.type == pygame.KEYDOWN:
        self._ui.switchState(MainMenu(self._ui))
        return

    super(WelcomeScreen, self).handleEvents(events)

class MainMenu(SimpleScreen, Menu):
  """The main menu screen - interactable"""

  def __init__(self, ui):
    super(MainMenu, self).__init__(ui, "assets/mainmenu.png")

  def handleEvents(self, events):
    """Handle user input events"""
    for e in events:
      if e.type == pygame.KEYDOWN:
        if e.key == pygame.K_c:
          self._ui.pushState(CharacterSelectScreen(self._ui))

    return super(MainMenu, self).handleEvents(events)

  def userSelect(self):
    # Switch to the level select menu
    self._ui.pushState(LevelSelectMenu(self._ui))

class TutorialScreen(SimpleScreen, Menu):
  """A tutorial screen"""

  def __init__(self, ui, basename, tutorialFiles, tutorialPage=0):
    """Accept a level base name and a list of image files"""
    # Initialize the background with the current page
    super(TutorialScreen, self).__init__(ui, tutorialFiles[tutorialPage])

    self.basename = basename
    self.tutorialFiles = tutorialFiles
    self.tutorialPage = tutorialPage

  def handleEvents(self, events):
    """Handle user input for moving through the tutorial"""
    for e in events:
      if e.type == pygame.KEYDOWN:
        if e.key == pygame.K_SPACE:
          # Skip the tutorial
          self.userSkip()
        elif e.key == pygame.K_RIGHT:
          # Move to the next page of the tutorial to or the level splash screen
          # if the tutorial is complete.
          self.userNext()
        elif e.key == pygame.K_LEFT:
          # Move to the previous page of the tutorial
          self.userBack()

    super(TutorialScreen, self).handleEvents(events)

  def userSkip(self):
    """Skip the next tutorial screens and switch directly to the level"""
    # Remove the accumulated pages from the stack
    for _ in xrange(self.tutorialPage):
      self.closeScreen()

    # Switch to the level screen
    self._ui.switchState(LevelSplashScreen(self._ui, self.basename))

  def userNext(self):
    """Move to next tutorial page"""
    # If this isn't the last page, advance to the next page
    if self.tutorialPage < len(self.tutorialFiles) - 1:
      self._ui.pushState(TutorialScreen(self._ui, self.basename,
        self.tutorialFiles, self.tutorialPage + 1))
    # Otherwise, go to the level screen
    else:
      self.userSkip()

class LevelSelectMenu(SimpleScreen, Menu):
  """The level select menu"""

  levelList = [
    ["level100", "level101", "level102", "level103", "level104"],
    ["level200", "level201", "level202", "level203", "level204"],
    ["level300", "level301", "level302", "level303", "level304"],
    ["level400", "level401", "level402", "level403", "level404"],
    ["level500", "level501", "level502", "level503", "level504"]
  ]

  # A list of tutorials for each level
  # Each sublist contains individual image files for that level's tutorials.
  tutList = [
    [
      "assets/intro_screen2.png",
      "assets/level01description.png",
      "assets/masterlevel1tutorial.png",
      "assets/masterlevel1tutorial1.png",
      "assets/masterlevel1tutorial2.png"
    ],
    [
      "assets/intro_screen2.png",
      "assets/level02description.png",
      "assets/masterlevel2tutorial.png",
      "assets/masterlevel2tutorial1.png"
    ],
    [
      "assets/intro_screen2.png",
      "assets/level03description.png",
      "assets/masterlevel3tutorial.png",
      "assets/masterlevel3tutorial1.png"
    ],
    [
      "assets/intro_screen2.png",
      "assets/level04description.png",
      "assets/masterlevel4tutorial.png",
      "assets/masterlevel4tutorial1.png"
    ],
    [
      "assets/intro_screen2.png",
      "assets/level05description.png",
      "assets/masterlevel5tutorial.png",
      "assets/masterlevel5tutorial1.png",
      "assets/masterlevel5tutorial2.png",
    ]
  ]

  def __init__(self, ui):
    super(LevelSelectMenu, self).__init__(ui, "assets/levelmenu.png")

  def handleEvents(self, events):
    """Handle user input events"""
    for e in events:
      if e.type == pygame.KEYDOWN:
        if e.key == pygame.K_1: # level one
          self.userSelectLevel(self.levelList[0][0], self.tutList[0])
        elif e.key == pygame.K_2: # level two
          self.userSelectLevel(self.levelList[1][0], self.tutList[1])
        elif e.key == pygame.K_3: # level three
          self.userSelectLevel(self.levelList[2][0], self.tutList[2])
        elif e.key == pygame.K_4: # level four
          self.userSelectLevel(self.levelList[3][0], self.tutList[3])
        elif e.key == pygame.K_5: # level five
          self.userSelectLevel(self.levelList[4][0], self.tutList[4])

    super(LevelSelectMenu, self).handleEvents(events);

  def userSelectLevel(self, basename, tutorialfiles):
    """Start the tutorial for the level that the user selected"""
    self._ui.pushState(TutorialScreen(self._ui, basename, tutorialfiles))

  def draw(self):
    """Draw the level select menu"""
    # Draw the background
    super(LevelSelectMenu, self).draw()

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
      # Draw the player sprite
      self._ui.spritesheet.tileCoord("person.png", 1, 0)
      glVertex3f(3, -3, 1)

      self._ui.spritesheet.tileCoord("person.png", 0, 0)
      glVertex3f(9, -3, 1)

      self._ui.spritesheet.tileCoord("person.png", 0, 1)
      glVertex3f(9, 3, 1)

      self._ui.spritesheet.tileCoord("person.png", 1, 1)
      glVertex3f(3, 3, 1)

    glEnd()

class LevelSplashScreen(SimpleScreen, Menu):
  """The splash screen that appears before starting a level"""

  def __init__(self, ui, basename):
    super(LevelSplashScreen, self).__init__(ui, "assets/background2.png")
    self.basename = basename

  def switchToLevel(self, newLevelName):
    self._ui.popState()
    self._ui.switchState(LevelSplashScreen(self._ui, newLevelName))

  def userSelect(self):
    self._ui.pushState(LevelScreen(self._ui, self, self.basename))

def main(name="", levelName=None):
  """Create and run the UI."""
  ui = UI()
  if levelName is None:
    ui.pushState(WelcomeScreen(ui))
  else:
    print "Directly loading %s" % levelName
    ui.pushState(LevelSplashScreen(ui, levelName))
  ui.run()

if __name__ == "__main__":
  frozen = getattr(sys, "frozen", "")
  if not frozen:
    os.chdir("..") # For locating assets

  print "Mumei running on", os.name
  if os.name == "nt":
    print "Increasing the stack size to 64MB..."
    # Windows 64 fix, see http://stackoverflow.com/questions/2917210/
    threading.stack_size(67108864)
    thread = threading.Thread(target=main, args=sys.argv)
    thread.start()
  else:
    main(*sys.argv)
