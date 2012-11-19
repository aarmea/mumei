"""
Interfaces for texture atlases
"""

import csv

from OpenGL.GL import *
import pygame

from texture import Texture

IMAGE_SUFFIX = "-0.png"
TILEMAP_SUFFIX = ".csv"

class TextureAtlas(object):
  """An interface for texturing quads with tiles from a single texture"""

  def __init__(self, texture, tilew, tileh):
    # Load the texture
    self.__texture = texture
    
    # Set the size of each texture
    self._tilew = tilew
    self._tileh = tileh

    # Calculate placement parameters
    self.__es = 1.0 / self.__texture.w
    self.__et = 1.0 / self.__texture.h
    self.__htiles = self.__texture.w / self._tilew
    self.__vtiles = self.__texture.h / self._tileh
    self.__ntiles = self.__htiles * self.__vtiles

  def reload(self):
    """Reload the backing texture from the surface data."""
    self.__texture.reload()

  def subsurface(self, rect):
    """Return a subsurface for the given sprite."""
    return self.__texture.surface.subsurface(rect)

  def bind(self):
    """Bind this tile set."""
    self.__texture.bind()

  def tileCoord(self, s, t, u, v):
    """Set the texture coordinates for the given tile."""
    assert s < self.__htiles
    assert t < self.__vtiles
    assert u >= 0.0 and u <= 1.0
    assert v >= 0.0 and v <= 1.0
    glTexCoord2f((s + u) * self._tilew * self.__es,
      (self.__texture.h - (t + 1.0 - v) * self._tileh) * self.__et)

class TileSet(TextureAtlas):
  """An interface for texturing quads with tiles from a single texture"""

  def __init__(self, path, prefix):
    # TODO: handle multiple spritesheets
    texture = Texture(path + prefix + IMAGE_SUFFIX)

    # Parse the *.csv file
    self.__images = dict()
    with open(path + prefix + TILEMAP_SUFFIX) as file_:
      csvFile = csv.reader(file_)

      for meta in csvFile:
        # Parse each individual element
        # Format: __images[sprite name] = (sheet file, top left corner, size)
        self.__images[meta[0]] = (meta[1], (int(meta[2]), int(meta[3])),
          (int(meta[4]), int(meta[5])))

      file_.close()

    # Pick a sprite and assume all the other sprites are the same size
    tilew, tileh = self.__images.values()[0][2]

    # Call the parent's constructor
    super(TileSet, self).__init__(texture, tilew, tileh)

  def subsurface(self, spriteName):
    """Return a subsurface for the given sprite."""
    rect = pygame.Rect(self.__images[spriteName][1] +
      (self._tilew, self._tileh))
    return super(TileSet, self).subsurface(rect)

  def tileCoord(self, spriteName, u, v):
    """Set the texture coordinates for the given tile."""
    s = self.__images[spriteName][1][0] / self._tilew
    t = self.__images[spriteName][1][1] / self._tileh
    super(TileSet, self).tileCoord(s, t, u, v)

class CharacterSet(TextureAtlas):
  """An interface for texturing quads with ASCII characters from a texture"""

  def __init__(self, filename):
    texture = Texture(filename)

    # A CharacterSet font image is 16 characters by 16 characters
    charw = texture.w / 16
    charh = texture.h / 16

    super(CharacterSet, self).__init__(texture, charw, charh)

  def tileCoord(self, char, u, v):
    """Set the texture coordinates from an ASCII code."""
    # ord(character) returns the character code of the character
    t, s = divmod(ord(char), 16)
    super(CharacterSet, self).tileCoord(s, t, u, v)
