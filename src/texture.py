"""
A OpenGL texture class
"""

from OpenGL.GL import *
import pygame

class Texture(object):
  """An OpenGL texture"""

  def __init__(self, file_):
    # Load and allocate the texture
    self.surface = pygame.image.load(file_).convert_alpha()
    self.__texture = glGenTextures(1)
    self.reload()

  def reload(self):
    # Set up the texture
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, self.__texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.w, self.h, 0, GL_RGBA,
      GL_UNSIGNED_BYTE, pygame.image.tostring(self.surface, "RGBA", True))

  def bind(self):
    glBindTexture(GL_TEXTURE_2D, self.__texture)

  w = property(lambda self: self.surface.get_width())
  h = property(lambda self: self.surface.get_height())
