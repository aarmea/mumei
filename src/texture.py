"""
A OpenGL texture class
"""

from OpenGL.GL import *
import pygame

class Texture(object):
  """An OpenGL texture"""

  def __init__(self, file_):
    """Allocate and load the texture"""
    self.surface = pygame.image.load(file_).convert_alpha()
    self.__texture = glGenTextures(1)
    self.reload()

  def __del__(self):
    """Release the texture"""
    glDeleteTextures([self.__texture])

  def reload(self):
    """Load the texture"""
    glBindTexture(GL_TEXTURE_2D, self.__texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.w, self.h, 0, GL_RGBA,
      GL_UNSIGNED_BYTE, pygame.image.tostring(self.surface, "RGBA", True))

  def bind(self):
    """Make the texture active in the current OpenGL context"""
    glBindTexture(GL_TEXTURE_2D, self.__texture)

  w = property(lambda self: self.surface.get_width())
  h = property(lambda self: self.surface.get_height())
