import csv
from OpenGL.GL import *
import pygame

import c.error
import c.scanner
import c.parser
import c.tacgen
import vm.tactrans
import vm.bytecode

import levelobj
from textureatlas import *
from textbox import *

SAMPLE_CODE = """extern int move;

int main()
{
  int i;

  while (1) {
    i = 0;
    while (i < 4) {
      move = 1;
      i = i + 1;
    }
    while (i < 8) {
      move = 0xFFFF;
      i = i + 1;
    }
  }

  return 0;
}
"""

class Level(object):
  """A level"""

  levelDir = "../assets/levels/"

  def __init__(self, ui, levelFile):
    self.__ui = ui
    self._height = 0
    self._width = 0
    self._objects = [ [] ]
    self._startPos = (0, 0)
    self._doorPos = (0, 0)

    # Temporary screen move stuff
    self.t = 0.0
    self.x = 0.0
    self.y = 0.0
    self.xrot = 15.0
    self.yrot = 20.0
    self.botx = 0
    self.botz = 1

    # Load level assets
    self.spritesheet = TileSet("../assets/", "spritesheet")
    self.charset = CharacterSet("../assets/font.png")
    self.load(levelFile)

    self._text = TextEditor((0, 5.75), (43, 48), self.charset, SAMPLE_CODE)

    # Spawn a player
    self._player = levelobj.Player(self._startPos, self.spritesheet)

    self._vars = {}
    self.procRunning = False

  def load(self, levelFile):
    """Load a level from a CSV file."""
    with open(self.levelDir + levelFile, 'rb') as file:
      csvFile = csv.reader(file)
      objects = []
      for y, row in enumerate(csvFile):
        # Update the level's dimensions
        self._height += 1
        if len(row) > self._width:
          self._width = len(row)

        # Add the elements at each cell to a temporary representation
        for x, cell in enumerate(row):
          objects.append(levelobj.NAMES.get(cell,
            levelobj.LevelObject)((x,y), self.spritesheet))

      # Resize the self._objects to the size of the level
      self._objects = [[levelobj.LevelObject((x,y), self.spritesheet)
                        for y in xrange(self._height)]
                        for x in xrange(self._width)]

      for obj in objects:
        # Invert the y position
        obj.move((obj._pos[0], self._height - obj._pos[1]))

        # Get the start position
        if isinstance(obj, levelobj.Start):
          self._startPos = obj._pos

        # Get the door position
        if isinstance(obj, levelobj.Door):
          self._doorPos = obj._pos

        # Convert the temporary objects to the 2D list self._objects
        self._objects[int(obj._pos[0])-1][int(obj._pos[1])-1] = obj

      self.x = -self._width / 2
      self.y = -self._height / 2

      print "Level: loaded", levelFile
      file.close()

  def compile(self):
    """Compile the source code in the text box, loading it into the
    processor."""
    # Get the source code
    source = self._text.text

    print "Compiling..."

    # Compile
    try:
      tokens = list(c.scanner.tokens(c.scanner.scan(source)))
      syntree = c.parser.parse(tokens)
      tac = syntree.accept(c.tacgen.TACGenerator())
      words, labels = vm.tactrans.translate(tac)
    except c.error.CompileError, e:
      print "compile error:", e
      return False
    except BaseException, e:
      print "unhandled compile error:", e
      return False

    print "Code compiled successfully"

    # Create a new processor
    self._proc = vm.bytecode.Processor(memWords=256)

    # Load the bytecode into memory
    for addr, word in enumerate(words):
      self._proc.setMem(addr, word)

    print "Linking..."

    # Link to the bytecode
    self._vars = {}
    for var in ("main", "move"):
      try:
        self._vars[var] = labels[var]
      except KeyError, e:
        print "undefined reference to `%s'" % e.args[0]
        return False

    # Set IP to the entry point
    entry = self._vars["main"]
    self._proc.setReg(self._proc.REG_IP, entry)

    # Set the default value for move
    moveAddr = self._vars["move"]
    self._proc.setMem(moveAddr, 0)

    print "Code linked successfully"

    return True

  def handleEvents(self, events):
    """Handle keyboard input."""
    for e in events:
      if e.type == pygame.QUIT:
        return True
      elif e.type == pygame.KEYDOWN:
        if e.key == pygame.K_ESCAPE:
          self.__ui.popState()
          break

        elif e.key == pygame.K_F5:
          self.procRunning = self.compile()

        # Temporary screen move stuff, trigger with right alt
        elif pygame.key.get_mods() & pygame.KMOD_RALT:
          if e.key == pygame.K_LEFT:
            self.x -= 0.5
          elif e.key == pygame.K_RIGHT:
            self.x += 0.5
          elif e.key == pygame.K_UP:
            self.y += 0.5
          elif e.key == pygame.K_DOWN:
            self.y -= 0.5
          elif e.key == pygame.K_w:
            self.xrot -= 5
          elif e.key == pygame.K_s:
            self.xrot += 5
          elif e.key == pygame.K_a:
            self.yrot -= 5
          elif e.key == pygame.K_d:
            self.yrot += 5
          elif e.key == pygame.K_i:
            pass
          elif e.key == pygame.K_j:
            self._player.relMove(self, (-1, 0))
          elif e.key == pygame.K_k:
            pass
          elif e.key == pygame.K_l:
            self._player.relMove(self, (1, 0))

        else:
          # Send all other keypresses to the text editor
          self._text.handleKeyPress(e.key, e.unicode)
    return False

  def draw(self, time):
    """Render the level interface."""
    # Step the processor
    if self.procRunning:
      try:
        self._proc.step()
      except BaseException, e:
        self.procRunning = False
        print "processor error:", e

      # Get the current move
      moveAddr = self._vars["move"]
      move = self._proc.getMem(moveAddr)

      # Sign extend
      if (move >= 0x8000):
        move = ~move + 0xFFFF;

      # Move the player
      self._player.relMove(self, (move, 0))

    # Draw
    glClearColor(0, 0, 1, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Temporary screen move stuff
    glTranslate(self.x * 3 / 2 - 0.5, (self.y - 1), 0)
    glRotate(self.xrot, 1, 0, 0)
    glRotate(self.yrot, 0, 1, 0)

    # Draw the static level
    for row in self._objects:
      for block in row:
        block.draw()

    # Draw the movable objects
    self._player.draw()

    # Draw the editor
    self._text.draw()
