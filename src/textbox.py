"""
The text editor visible in the level interface.
"""

from OpenGL.GL import *
import pygame

from textureatlas import *

class TextBox(object):
  """A read-only OpenGL text box"""

  # CHOPL, CHOPR = 0.125, 0.875
  CHOPL, CHOPR = 0.1875, 0.8125
  SCALEX = abs(CHOPL-CHOPR)

  def __init__(self, pos, size, charset, text):
    self.__displayList = None
    self._buffer = []
    self._pos = pos
    self._size = size
    self._charset = charset

    self._setText(text)

  def _setText(self, text):
    # Convert the text input into the _chars array of strings
    self._buffer = [list(thing) for thing in text.split("\n")]
    self._cursorPos = (len(self._buffer)-1, len(self._buffer[-1]))
    self.update()

  def _getText(self):
    """Return a string containing the contents of the buffer."""
    return "\n".join("".join(row) for row in self._buffer)

  def update(self):
    """Update the display list"""
    # Free the old display list
    if self.__displayList is not None:
      glDeleteLists(self.__displayList, 1)

    # Create a new display list
    self.__displayList = glGenLists(1)
    glNewList(self.__displayList, GL_COMPILE)
    self.render()
    glEndList()

  def render(self):
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(self._pos[0], self._pos[1], 0)
    glScalef(0.25, 0.25, 1)

    self._charset.bind()
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glEnable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)

    glBegin(GL_QUADS)
    for line in xrange(self._size[1]):
      for col in xrange(self._size[0]):
        try:
          char = self._buffer[line][col]
        except IndexError:
          char = " "

        # Draw a quad
        self._charset.tileCoord(char, self.CHOPL, 0)
        glVertex3f(col*self.SCALEX, -line, 0)

        self._charset.tileCoord(char, self.CHOPR, 0)
        glVertex3f((col+1)*self.SCALEX, -line, 0)

        self._charset.tileCoord(char, self.CHOPR, 1)
        glVertex3f((col+1)*self.SCALEX, -line+1, 0)

        self._charset.tileCoord(char, self.CHOPL, 1)
        glVertex3f(col*self.SCALEX, -line+1, 0)
    glEnd()

  def draw(self):
    if self.__displayList is None:
      self.update()

    glCallList(self.__displayList)

  text = property(_getText)

class LineNumbers(TextBox):
  """Line numbers that can be placed next to a TextBox or TextEditor"""

  def __init__(self, pos, lines, charset):
    rows, cols = lines, len(str(lines))
    string = ""
    for num in xrange(lines):
      string += '|' + str(num).rjust(cols, ' ') + "|\n"
    super(LineNumbers, self).__init__(pos, (cols+2, rows), charset, string)

class TextEditor(TextBox):
  """An OpenGL text editor"""

  def handleKeyPress(self, key, uni=-1):
    # If the unicode character was not given, generate it from the key
    if uni == -1:
      uni = chr(key)

    row, col = self._cursorPos

    # Parse keys
    if key == pygame.K_LEFT:
      if col > 0:
        self._cursorPos = (row, col-1)
    elif key == pygame.K_RIGHT:
      if col < len(self._buffer[row]):
        self._cursorPos = (row, col+1)
    elif key == pygame.K_UP:
      if row > 0:
        if col < len(self._buffer[row-1]):
          self._cursorPos = (row-1, col)
        else:
          self._cursorPos = (row-1, len(self._buffer[row-1]))
    elif key == pygame.K_DOWN:
      if row < len(self._buffer)-1:
        if col < len(self._buffer[row+1]):
          self._cursorPos = (row+1, col)
        else:
          self._cursorPos = (row+1, len(self._buffer[row+1]))
    elif key == pygame.K_BACKSPACE:
      # Backspace
      if col == 0:
        # Beginning of line

        # Do nothing if at the beginning of the document
        if row == 0: return

        oldLineLen = len(self._buffer[row-1])
        self._buffer[row-1].extend(self._buffer[row])
        self._buffer.pop(row)
        self._cursorPos = (row-1, oldLineLen)
      else:
        self._buffer[row].pop(col-1)
        self._cursorPos = (row, col-1)
      self.update()
    elif key == pygame.K_DELETE:
      # Backspace
      if col == len(self._buffer[row]):
        # End of line

        # Do nothing if at the end of the document
        if row == len(self._buffer)-1: return

        self._buffer[row].extend(self._buffer[row+1])
        self._buffer.pop(row+1)
      else:
        self._buffer[row].pop(col)
      self.update()
    elif key == pygame.K_RETURN:
      # Enter/Return
      self._buffer.insert(row+1, self._buffer[row][col:])
      self._buffer[row] = self._buffer[row][:col]
      self._cursorPos = (row+1, 0)
      self.update()
    elif key >= 0x20 and key <= 0x7E:
      # Printable keys
      try:
        self._buffer[row].insert(col, uni)
      except IndexError:
        self._buffer[row].append(uni)
      self._cursorPos = (row, col+1)
      self.update()

  def draw(self):
    super(TextEditor, self).draw()

    # Draw the cursor
    glDisable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    if True:
      glColor4f(1, 1, 1, 1)
      glVertex3f((self._cursorPos[1]+0.2)*self.SCALEX, -self._cursorPos[0], 0)
      glVertex3f((self._cursorPos[1]+0.8)*self.SCALEX, -self._cursorPos[0], 0)
      glVertex3f((self._cursorPos[1]+0.8)*self.SCALEX, -self._cursorPos[0]+0.125, 0)
      glVertex3f((self._cursorPos[1]+0.2)*self.SCALEX, -self._cursorPos[0]+0.125, 0)
    glEnd()

