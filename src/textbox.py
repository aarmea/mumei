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
    self._chars = text.split("\n")

  def draw(self):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(self._pos[0], self._pos[1], 0)
    glScalef(0.25, 0.25, 1)

    self._charset.bind()
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glDisable(GL_DEPTH_TEST)

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

class TextEditor(TextBox):
  """An OpenGL text editor"""

  def draw(self):
    super(TextEditor, self).draw()
