"""
Error classes for the C compiler
"""

class CompileError(Exception):
  """An error encountered while compiling a program"""

  def __init__(self, pos, msg):
    Exception.__init__(self, pos, msg)

  def __str__(self):
    return "%s: %s" % (self.pos, self.msg)

  pos = property(lambda self: self.args[0])
  """The position of the error"""

  msg = property(lambda self: self.args[1])
  """The error message"""

class CompileWarning(CompileError):
  """A warning raised while compiling a program"""
