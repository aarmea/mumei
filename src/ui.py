from OpenGL.GL import *
import pygame

from textureatlas import CharacterSet, TileSet

class UI(object):
  """The main user interface object"""

  def __init__(self):
    pygame.init()

    # Create the window
    self.screen = pygame.display.set_mode((1024, 768),
      pygame.OPENGL | pygame.DOUBLEBUF)

    # Load the tile sets
    self.spritesheet = TileSet("assets/", "spritesheet")
    self.characterSet = CharacterSet("assets/font.png")

    # Set up the window
    icon = self.spritesheet.subsurface("pickle.png")
    icon = pygame.transform.scale(icon, (32, 32))
    pygame.display.set_icon(icon)

    pygame.display.set_caption("Mumei")
    pygame.mouse.set_visible(False)
    pygame.key.set_repeat(250, 50)

    # Set up the projection matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1024 / 64 / 2, 1024 / 64 / 2, -768 / 64 / 2, 768 / 64 / 2, -10, 10)

    # Set up the initial player state
    self.hair = 0
    self.head = 0
    self.shirt = 0
    self.pants = 0

    # Set up the initial screen state
    self.stateStack = []

  def pushState(self, state):
    """Add a state to the state stack. The new state will become the active
    state."""
    self.stateStack.append(state)

  def popState(self):
    """Remove a state from the state stack. The previous state will become the
    active state."""
    self.stateStack.pop()

  def switchState(self, state):
    """Change the state on the top of the stack to the given stae."""
    self.popState()
    self.pushState(state)

  def run(self):
    """Run the main UI loop."""
    clock = pygame.time.Clock()
    time = 0.0

    while len(self.stateStack) > 0:
      # Pass events to the current state
      currentState = self.stateStack[-1]
      currentState.handleEvents(pygame.event.get())

      # Update the current state
      time += clock.tick()
      currentState.update(time)

      # Draw the current state
      currentState.draw()
      pygame.display.flip()
