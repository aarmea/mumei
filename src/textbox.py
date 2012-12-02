"""
A box that displays text on screen and its associated subclasses
"""

from OpenGL.GL import *
from OpenGL.GL.ARB.vertex_buffer_object import *
from OpenGL.arrays import ArrayDatatype
import numpy
import pygame

from textureatlas import *

COLOR_WHITE = (1, 1, 1, 1)

class TextBox(object):
  """A read-only OpenGL text box"""

  CHOPL, CHOPR = 0.1875, 0.8125
  SCALEX = abs(CHOPL-CHOPR)

  def __init__(self, ui, pos, rows, cols, color=COLOR_WHITE):
    """Initialize the vertex buffer, text array, and texture coordinate
    array"""
    self._pos = pos
    self._rows = rows
    self._cols = cols
    self._color = color
    self._charset = ui.characterSet

    # Set up the vertex buffer
    self.__vertexBuffer = glGenBuffersARB(1)
    glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.__vertexBuffer)

    # Generate the vertices
    vertices = []
    for row in xrange(rows):
      for col in xrange(cols):
        vertices.append((col * self.SCALEX, -row, 0))
        vertices.append(((col + 1) * self.SCALEX, -row, 0))
        vertices.append(((col + 1) * self.SCALEX, -row + 1, 0))
        vertices.append((col * self.SCALEX, -row + 1, 0))

    vertexArray = numpy.array(vertices, dtype=numpy.float32)

    # Load the vertices into the vertex buffer
    glBufferDataARB(GL_ARRAY_BUFFER_ARB,
      ArrayDatatype.arrayByteCount(vertexArray),
      ArrayDatatype.voidDataPointer(vertexArray), GL_STATIC_DRAW)

    # Initialize the text array
    self._textArray = numpy.zeros((rows, cols), dtype=numpy.uint8)

    # Set up the texture coordinate buffer
    self.__texCoordBuffer = glGenBuffersARB(1)
    glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.__texCoordBuffer)

    # Initialize all texture coordinates to zero
    self._texCoordArray = numpy.zeros((rows, cols, 4, 2),
      dtype=numpy.float32)

    # Force the buffer to be reloaded on the next draw
    self._dirty = True

  def __del__(self):
    """Release the array buffers"""
    buffers = [self.__vertexBuffer, self.__texCoordBuffer]
    glDeleteBuffersARB(len(buffers), buffers)

  def __getitem__(self, (row, col)):
    """Get the character at the given position"""
    return chr(self._textArray[row, col])

  def __setitem__(self, (row, col), char):
    """Set the character at the given position to the given value"""
    # Store the character
    self._textArray[row, col] = ord(char)

    # Set the texture coordinates for this character position
    u, v = self._charset.getCoord(char, self.CHOPL, 0)
    self._texCoordArray[row, col, 0, 0] = u
    self._texCoordArray[row, col, 0, 1] = v
    u, v = self._charset.getCoord(char, self.CHOPR, 0)
    self._texCoordArray[row, col, 1, 0] = u
    self._texCoordArray[row, col, 1, 1] = v
    u, v = self._charset.getCoord(char, self.CHOPR, 1)
    self._texCoordArray[row, col, 2, 0] = u
    self._texCoordArray[row, col, 2, 1] = v
    u, v = self._charset.getCoord(char, self.CHOPL, 1)
    self._texCoordArray[row, col, 3, 0] = u
    self._texCoordArray[row, col, 3, 1] = v

    self._dirty = True

  def draw(self):
    """Render the textbox"""
    # Reload the texture coordinate buffer if anything changed
    if self._dirty:
      # Bind and load the buffer
      glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.__texCoordBuffer)
      glBufferDataARB(GL_ARRAY_BUFFER_ARB,
        ArrayDatatype.arrayByteCount(self._texCoordArray),
        ArrayDatatype.voidDataPointer(self._texCoordArray), GL_DYNAMIC_DRAW)

      glBindBufferARB(GL_ARRAY_BUFFER, 0)

      self._dirty = False

    # Set up transformations
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glTranslatef(self._pos[0], self._pos[1], 0)
    glScalef(0.25, 0.25, 1)

    # Set up the foreground color
    glColor4f(*self._color)

    # Set up the texture
    glEnable(GL_TEXTURE_2D)
    self._charset.bind()
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    # Enable vertex and texture arrays
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    # Set the vertex buffer for rendering
    glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.__vertexBuffer)
    glVertexPointer(3, GL_FLOAT, 0, None)

    # Set the texture coordinate buffer for rendering
    glBindBufferARB(GL_ARRAY_BUFFER_ARB, self.__texCoordBuffer)
    glTexCoordPointer(2, GL_FLOAT, 0, None)

    # Unbind the active buffer--pointers are already specified
    glBindBufferARB(GL_ARRAY_BUFFER, 0)

    # Render over everything else
    glDisable(GL_DEPTH_TEST)

    # Render
    glDrawArrays(GL_QUADS, 0, self._cols * self._rows * 4)

    # Disable vertex and texture arrays
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)

  def _getTextLine(self, row):
    """Return the line of text at the given row"""
    nonzeros = numpy.transpose(self._textArray[row].nonzero())
    if not len(nonzeros):
      size = 0
    else:
      size = nonzeros[-1][0] + 1
    return "".join(chr(self._textArray[row, x]) for x in xrange(size))

  def _getTextLineCount(self):
    """Return the number of lines of text in the buffer"""
    # Return the row of the last non-zero character
    nonzeros = numpy.transpose(self._textArray.nonzero())
    if not len(nonzeros):
      return 0
    else:
      return nonzeros[-1][0] + 1

  def __getText(self):
    """Return a string containing the contents of the buffer. Null characters
    outside of the text are discarded."""
    return "\n".join(self._getTextLine(row) for row in
      xrange(self._getTextLineCount()))

  def __setText(self, text):
    """Set the buffer to contain the given text, truncating lines as
    necessary."""
    # Zero the text and texture coordinate arrays
    self._textArray[:] = 0
    self._texCoordArray[:] = 0

    # Split the text into lines
    lines = text.split("\n")

    # Set the characters at every valid position
    for row in xrange(min(len(lines), self._rows)):
      for col in xrange(min(len(lines[row]), self._cols)):
        self[row, col] = lines[row][col]

  text = property(__getText, __setText)

class LineNumbers(TextBox):
  """Line numbers that can be placed next to a TextBox or TextEditor"""

  def __init__(self, ui, pos, lines, color=COLOR_WHITE):
    rows, cols = lines, len(str(lines))
    super(LineNumbers, self).__init__(ui, pos, rows, cols + 2, color)

    # Initialize the line number text
    text = ""
    for num in xrange(1, lines + 1):
      text += "|%s|\n" % str(num).rjust(cols, " ")

    self.text = text

class TextEditor(TextBox):
  """An OpenGL text editor"""

  # The initial cursor position
  _cursorPos = (0, 0)

  # Array helpers
  @staticmethod
  def __shiftRows(array, row, off):
    """Copy rows of an array from the given row to the bottom down by the given
    offset, overwriting the rows below."""
    bottomRows = array[row:].copy()
    bottomRows.resize(bottomRows.shape[0] - off, *bottomRows.shape[1:])
    array[row + off:] = bottomRows

  @staticmethod
  def __shiftRowCols(array, row, col, off):
    """Copy columns of an array from the given column to the right edge right by
    the given amount, overwriting the columns to the right."""
    rightCols = array[row, col:].copy()
    rightCols.resize(rightCols.shape[0] - off, *rightCols.shape[1:])
    array[row, col + off:] = rightCols

  @staticmethod
  def __copyRowCols(array, row, col, off):
    """Copy the columns of an array from the given column to the right edge on
    the given row to the start of the row down by the given offset, overwriting
    its contents."""
    rightCols = array[row, col:].copy()
    rightCols.resize(*array.shape[1:])
    array[row + off, :] = rightCols

  # Editor-specific helpers
  def __shiftTextRows(self, row, off):
    """Copy rows of text down by the given offset."""
    TextEditor.__shiftRows(self._textArray, row, off)
    TextEditor.__shiftRows(self._texCoordArray, row, off)

    self._dirty = True

  def __shiftTextRowCols(self, row, col, off):
    """Copy columns of text on the given row right by the given offset."""
    TextEditor.__shiftRowCols(self._textArray, row, col, off)
    TextEditor.__shiftRowCols(self._texCoordArray, row, col, off)

    self._dirty = True

  def __copyTextRowCols(self, row, col, off):
    """Copy columns of text on the given row down to the start of the row down
    by the given offset."""
    TextEditor.__copyRowCols(self._textArray, row, col, off)
    TextEditor.__copyRowCols(self._texCoordArray, row, col, off)

    self._dirty = True

  def __eraseText(self, slice_):
    """Erase the text in the given extended slice."""
    self._textArray[slice_] = 0
    self._texCoordArray[slice_] = 0

    self._dirty = True

  # Editor functions
  def __moveCursor(self, newRow, newCol):
    """Move the cursor to the given position"""
    row, col = self._cursorPos

    # Check the row
    if newRow < 0:
      row = 0
    elif newRow > self._getTextLineCount():
      row = self._getTextLineCount()
    else:
      row = newRow

    # Check the column
    if newCol < 0:
      col = 0
    elif newCol > len(self._getTextLine(row)):
      col = len(self._getTextLine(row))
    else:
      col = newCol

    # Update the cursor position
    self._cursorPos = (row, col)

  def __insertCharacter(self, char):
    """Insert the given character at the cursor position"""
    row, col = self._cursorPos

    # Insert a newline if necessary
    if col == self._cols:
      self.__insertNewline()
      row, col = self._cursorPos

    # Shift everything to the right right by one column
    self.__shiftTextRowCols(row, col, 1)

    # Set the character
    self[row, col] = char

    # Update the cursor position
    self._cursorPos = (row, col + 1)

  def __insertNewline(self):
    """Insert a newline at the cursor position"""
    row, col = self._cursorPos

    # Copy everything below the current row down one row
    self.__shiftTextRows(row, 1)

    # Copy everything right of current column to the next row
    self.__copyTextRowCols(row, col, 1)

    # Erase everything after the newline in the current row
    self.__eraseText((row, slice(col, None, None)))

    # Update the cursor
    self._cursorPos = (row + 1, 0)

  def __deleteCharacter(self):
    """Delete the character at the cursor position"""
    row, col = self._cursorPos

    # Not at the end of a line
    if col < len(self._getTextLine(row)):
      # Shift everything to the right left by one column
      self.__shiftTextRowCols(row, col + 1, -1)

    # At the end of a line, but not at the end of the document
    elif row < self._getTextLineCount() - 1:
      # Copy the next row
      oldRow = self._textArray[row + 1].copy()
      oldRowCoords = self._texCoordArray[row + 1].copy()

      # Move the lower rows up
      self.__shiftTextRows(row + 2, -1)

      # Append the old row to the current row
      newRowLen = len(self._getTextLine(row))

      copyLen = self._cols - newRowLen
      self._textArray[row, newRowLen:] = oldRow[:copyLen]
      self._texCoordArray[row, newRowLen:] = oldRowCoords[:copyLen]

      self._dirty = True

  def handleKeyPress(self, key, uni=None):
    """Handle user input"""
    row, col = self._cursorPos

    # If the unicode character was not given, generate it from the key
    if uni is None:
      uni = chr(key)

    # Handle specific keys
    if key in (pygame.K_LEFT, pygame.K_BACKSPACE):
      # Handle wrapping
      if col == 0 and row != 0:
        self.__moveCursor(row - 1, self._cols)
      else:
        self.__moveCursor(row, col - 1)

      if key == pygame.K_BACKSPACE and (row > 0 or col > 0):
        self.__deleteCharacter()

    elif key == pygame.K_RIGHT:
      # Handle wrapping
      if col == len(self._getTextLine(row)):
        self.__moveCursor(row + 1, 0)
      else:
        self.__moveCursor(row, col + 1)

    elif key == pygame.K_UP:
      self.__moveCursor(row - 1, col)

    elif key == pygame.K_DOWN:
      self.__moveCursor(row + 1, col)

    elif key == pygame.K_HOME:
      self.__moveCursor(row, 0)

    elif key == pygame.K_END:
      self.__moveCursor(row, self._cols)

    elif key == pygame.K_DELETE:
      self.__deleteCharacter()

    elif key == pygame.K_RETURN:
      self.__insertNewline()

    # Insert printable keys
    elif key >= 0x20 and key <= 0x7E:
      self.__insertCharacter(uni)

  def draw(self):
    super(TextEditor, self).draw()

    # Draw the cursor
    row, col = self._cursorPos

    glDisable(GL_TEXTURE_2D)
    glBegin(GL_QUADS)
    if True:
      glColor4f(*COLOR_WHITE)
      glVertex3f((col + 0.2) * self.SCALEX, -row, 0)
      glVertex3f((col + 0.8) * self.SCALEX, -row, 0)
      glVertex3f((col + 0.8) * self.SCALEX, -row + 0.125, 0)
      glVertex3f((col + 0.2) * self.SCALEX, -row + 0.125, 0)
    glEnd()

