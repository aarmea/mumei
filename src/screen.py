import sys

from OpenGL.GL import *
import pygame

from texture import Texture

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

class SimpleScreen(Screen):
  """A screen with a single textured quad displaying a background image"""

  def __init__(self, ui, textureFile):
    super(SimpleScreen, self).__init__(ui)
    self._texture = Texture(textureFile)

  def draw(self):
    """Draw the menu background"""
    # Clear the screen
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_TEXTURE_2D)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    self._texture.bind()
    glBegin(GL_QUADS)
    if True:
      glColor4f(1, 1, 1, 1)
      glTexCoord2f(0.0, 0.0); glVertex2f(-8.0, -6.0)
      glTexCoord2f(1.0, 0.0); glVertex2f( 8.0, -6.0)
      glTexCoord2f(1.0, 1.0); glVertex2f( 8.0,  6.0)
      glTexCoord2f(0.0, 1.0); glVertex2f(-8.0,  6.0)
    glEnd()
