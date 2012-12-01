import random
import sys

from OpenGL.GL import *
import pygame
from time import sleep

import c.error
import c.scanner
import c.parser
import c.tacgen
import vm.tactrans
import vm.bytecode

from level import Level
from levelobj import Player, Robot
from screen import Screen
from textbox import LineNumbers, TextBox, TextEditor

LEVEL_DIR = "../assets/levels/"

EPSILON = 0.01
STEP_PERIOD = 10.0 #ms

class LevelScreen(Screen):
  """An interface for a level with a code editor and status panes"""

  def __init__(self, ui, parent, levelName):
    super(LevelScreen, self).__init__(ui)

    self._parent = parent
    self._levelName = levelName
    self._lastTime = 0

    # Load the level itself
    self._level = Level(self._ui, levelName)

    # Load the level assets
    with open(LEVEL_DIR + levelName + ".c", "rb") as sampleCode:
      self._sampleCode = sampleCode.read()
    with open(LEVEL_DIR + levelName + ".txt", "rb") as helpText:
      self._helpText = helpText.read()
    try:
      with open(LEVEL_DIR + levelName + "-hints.txt", "rb") as hints:
        self._hints = hints.read().split("\n")
    except IOError:
      self._hints = []
    with open("include.h", "rb") as headerFile:
      self.__header = headerFile.read()
      self.__headerLines = len(filter(lambda x: x == "\n", self.__header))

    # UI elements
    self._linesLabel = LineNumbers(self._ui, (0, 5.75), 47)
    self._editor = TextEditor(self._ui, (0.625, 5.75), (47, 47))
    self._debug = TextBox(self._ui, (0, 5.75), (47, 47))
    self._keysLabel = TextBox(self._ui, (-8, -1), (51, 2))
    self._infoLabel = TextBox(self._ui, (-8, -1.5), (51, 17))
    self._statusLabel = TextBox(self._ui, (-8, -6), (102, 1))

    self._debugView = False
    self._debugAddr = 0

    self._editor.text = self._sampleCode
    self._keysLabel.text = (
      "F1 hints | F2 reset code | F3 reset level | F5 run\n"
      "==================================================="
    )
    self._infoLabel.text = self._helpText
    self._statusLabel.text = "Ready"

    # Spawn players
    self.resetLevel()

  def resetLevel(self):
    """Reset the level state, starting the user at the beginning."""
    self._player = Player(self._ui, self._level, self._level.startPos)
    self._robot = Robot(self._ui, self._level, self._level.startPos)

  def resetCode(self):
    """Reset the code in the editor to the sample code."""
    self._editor.text = self._sampleCode

  def compileCode(self):
    """Compile the source code in the text box, loading it into the robot's
    processor."""
    # Get the source code
    source = self.__header + self._editor.text

    print source

    self._statusLabel.text = "Compiling..."

    # Compile the source code
    try:
      tokens = list(c.scanner.tokens(c.scanner.scan(source)))
      syntree = c.parser.parse(tokens)
      tac = syntree.accept(c.tacgen.TACGenerator())
      words, vars_ = vm.tactrans.translate(tac)
    except c.error.CompileError, e:
      pos = c.scanner.Position(e.pos.line-self.__headerLines, e.pos.col)
      e = c.error.CompileError(pos, e.msg)
      self._statusLabel.text = "Compile error: %s" % e
      return
    except BaseException, e:
      self._statusLabel.text = "Internal compiler error: %s" % e
      return

    self._statusLabel.text = "Code compiled successfully"

    # Load the code into the robot's processor
    try:
      self._robot.load(words, vars_)
    except BaseException, e:
      self._statusLabel.text = "Something went wrong: %s" % e
      return

    self._statusLabel.text = "Code loaded successully"

  def dumpProcessor(self, proc, startAddr):
    """Dump a processor's state"""
    text = ""
    width = 8
    ip = proc.getReg(proc.REG_IP)

    text += "MEMORY:"
    for addr in xrange(startAddr, min(proc.memWords, startAddr + 0x100)):
      if not (addr % width):
        text += "\n%03X:" % addr

      text += "%s%04X" % ('>' if addr == ip else ' ', proc.getMem(addr))

    text += "\n\nREGISTERS:\n"
    text += "  X0 %04X   X2 %04X        FL %04X   SP %04X\n" % \
      (proc.getReg(proc.REG_X0), proc.getReg(proc.REG_X2),
       proc.getReg(proc.REG_FL), proc.getReg(proc.REG_SP))
    text += "  X1 %04X   X3 %04X                  IP %04X\n" % \
      (proc.getReg(proc.REG_X1), proc.getReg(proc.REG_X3),
       proc.getReg(proc.REG_IP))

    text += "\nCYCLE: %d\n" % proc.cycle
    try:
      seq = proc.memSeq(ip)
      inst = str(vm.bytecode.Instruction.decode(seq))
    except vm.bytecode.InstructionError:
      inst = "(invalid)"
    text += "NEXT INSTRUCTION: %s\n" % inst

    return text

  def isComplete(self):
    """Check whether the level has been completed"""
    # The robot should not be moving
    if self._robot.direction != 0:
      return False

    # The robot should be at the destination door
    if (abs(self._robot._pos[0] - self._level.doorPos[0]) > EPSILON or
      abs(self._robot._pos[1] - self._level.doorPos[1]) > EPSILON):
      return False

    # The robot's color shold match the door color
    if self._robot.color != self._level.at(self._level.doorPos).color:
      return False

    return True

  def handleEvents(self, events):
    """Handle user input events"""
    for e in events:
      if e.type == pygame.KEYDOWN:
        if e.key == pygame.K_ESCAPE:
          self.closeScreen()
        elif pygame.key.get_mods() & (pygame.KMOD_RALT | pygame.KMOD_RCTRL):
          if e.key == pygame.K_q:
            sys.exit()
          elif e.key == pygame.K_UP:
            self._player.direction = 4
          elif e.key == pygame.K_LEFT:
            self._player.direction = 1
          elif e.key == pygame.K_DOWN:
            self._player.direction = 3
          elif e.key == pygame.K_RIGHT:
            self._player.direction = 2
        elif e.key == pygame.K_F1:
          random.shuffle(self._hints)
          try:
            self._statusLabel.text = "HINT: " + self._hints[0]
          except IndexError:
            self._statusLabel.text = "No hints available for this level"
        elif e.key == pygame.K_F2:
          self.resetCode()
          self._statusLabel.text = "Code reset to defaults"
        elif e.key == pygame.K_F3:
          self.resetLevel()
          self._statusLabel.text = "Level state reset to defaults"
        elif e.key == pygame.K_F5:
          if not self._robot.running:
            self.compileCode()
          else:
            self._statusLabel.text = \
              "Stop your code with F3 before running again"
        elif e.key == pygame.K_F8:
          self._debugView = not self._debugView
        elif self._debugView:
          if e.key == pygame.K_LEFT:
            if self._debugAddr > 0:
              self._debugAddr -= 0x100
          elif e.key == pygame.K_RIGHT:
            if self._debugAddr < self._robot.processor.memWords - 0x100:
              self._debugAddr += 0x100
        else:
          self._editor.handleKeyPress(e.key, e.unicode)
      elif e.type == pygame.KEYUP:
        self._player.direction = 0

    super(LevelScreen, self).handleEvents(events)

  def update(self, time):
    """Update the level state"""
    duration = time - self._lastTime
    steps = int(duration / STEP_PERIOD)

    while steps > 0:
      # Step the player and the robot
      self._player.step()
      self._robot.step()

      steps -= 1
      self._lastTime += STEP_PERIOD

    if self.isComplete():
      # Get the next level name
      subLevelNumber = int(self._levelName[-1:])
      if subLevelNumber == 4:
        newLevelName = "%s%d" % (self._levelName[:5], int(self._levelName[-3:]) + 100)
      else:
        newLevelName = "%s%d" % (self._levelName[:7], subLevelNumber + 1)

      self._statusLabel.text = "Level completed - loading %s" % newLevelName
      self.draw()
      pygame.display.flip()
      sleep(3) # so that the message is visible before the next level is loaded

      self._parent.switchToLevel(newLevelName)

  def draw(self):
    """Render the level and the interface"""
    # Clear the screen and reset the OpenGL state
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_TEXTURE_2D)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Set the level position on the screen
    glPushMatrix()
    glTranslate(-8.5, -2, 0)
    glRotate(15, 1, 0, 0)
    glRotate(20, 0, 1, 0)

    # Draw the level
    self._level.draw()

    # Draw the characters
    self._player.draw()
    self._robot.draw()

    glPopMatrix()

    # Draw the interface
    if not self._debugView:
      self._linesLabel.draw()
      self._editor.draw()
    else:
      self._debug.text = (self.dumpProcessor(self._robot.processor, self._debugAddr)
        + "\nPress the left and right arrow keys to\nchange memory pages.")
      self._debug.draw()
    self._keysLabel.draw()
    self._infoLabel.draw()
    self._statusLabel.draw()
