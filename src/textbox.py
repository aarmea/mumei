"""
The text editor visible in the level interface.
"""

from OpenGL.GL import *

from textureatlas import *

class TextBox(object):
  """A read-only OpenGL text box"""

  def __init__(self, pos, size, charset, text):
    self._chars = []
    self._pos = pos
    self._size = size
    self._charset = charset

    # Convert the text input into the _chars array of strings
    """
    string = ""
    for char in text:
      if char != "\n":
        string += char
      else:
        self._chars += string
        string = ""
    """
    self._chars = text.split("\n")

  def draw(self):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    self._charset.bind()

    glBegin(GL_QUADS)
    for line in xrange(self._size[1]):
      for col in xrange(self._size[0]):
        try:
          char = self._chars[line][col]
        except IndexError:
          char = " "

        # Draw a quad
        self._charset.tileCoord(char, 0, 0)
        glVertex3f(col, -line, 0)

        self._charset.tileCoord(char, 1, 0)
        glVertex3f(col+1, -line, 0)

        self._charset.tileCoord(char, 1, 1)
        glVertex3f(col+1, -line+1, 0)

        self._charset.tileCoord(char, 0, 1)
        glVertex3f(col, -line+1, 0)
    glEnd()

