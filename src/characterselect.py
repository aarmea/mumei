from OpenGL.GL import *
import pygame

from screen import SimpleScreen
from texture import Texture
from textureatlas import CharacterSet, TileSet

class CharacterSelectScreen(SimpleScreen):
  """A screen that allows the user to select their character's appearance"""

  NHAIRS = 6
  NHEADS = 4
  NSHIRTS = 2
  NPANTS = 2

  def __init__(self, ui):
    SimpleScreen.__init__(self, ui, "assets/charactermenu.png")

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
    """Handle user input"""
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

        elif e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
          self.closeScreen()

    SimpleScreen.handleEvents(self, events)

  def draw(self):
    """Draw the background image"""
    SimpleScreen.draw(self)

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
