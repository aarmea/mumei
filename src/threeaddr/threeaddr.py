"""
Three-address code instructions and helper classes
"""

class AutoGen(object):
  """An automatic identifier generator"""

  def __init__(self, prefix):
    self.prefix = prefix
    self.n = 0

  def next(self):
    n = self.n
    self.n += 1
    return "%s%d" % (self.prefix, self.n)

class Label(tuple):
  """A named jump target"""

  def __new__(cls, name):
    return tuple.__new__(cls, (name,))

  def __repr__(self):
    return "%s(name=%r)" % (type(self).__name__, self.name)

  name = property(lambda self: self[0])

class Word(tuple):
  """A literal word"""

  def __new__(cls, val):
    return tuple.__new__(cls, (val,))

  def __repr__(self):
    return "%s(val=%r)" % (type(self).__name__, self.val)

  val = property(lambda self: self[0])

class BeginFunc(tuple):
  """Begin a function, allocating the given number of words on the stack for
  local variables"""

  def __new__(cls, nwords):
    return tuple.__new__(cls, (nwords,))

  def __repr__(self):
    return "%s(nwords=%r)" % (type(self).__name__, self.nwords)

  nwords = property(lambda self: self[0])

class EndFunc(tuple):
  """End a function, using the given variable as the return value"""

  def __new__(cls, ret):
    return tuple.__new__(cls, (ret,))

  def __repr__(self):
    return "%s(src=%r)" % (type(self).__name__, self.ret)

  ret = property(lambda self: self[0])

class Assign(tuple):
  """An operation that assigns a source constant or variable to a destination
  variable"""

  def __new__(cls, dst, src):
    return tuple.__new__(cls, (dst, src))

  def __repr__(self):
    return "%s(dst=%r, src=%r)" % (type(self).__name__, self.dst, self.src)

  dst = property(lambda self: self[0])
  src = property(lambda self: self[1])

class PushParam(tuple):
  """An operation that pushes a variable onto the parameter stack for a future
  function call"""

  def __new__(cls, src):
    return tuple.__new__(cls, (src,))

  def __repr__(self):
    return "%s(src=%r)" % (type(self).__name__, self.src)

  src = property(lambda self: self[0])

class PopParams(tuple):
  """An operation that removes words from the parameter stack"""

  def __new__(cls, nwords):
    return tuple.__new__(cls, (nwords,))

  def __repr__(self):
    return "%s(nwords=%r)" % (type(self).__name__, self.nwords)

  nwords = property(lambda self: self[0])

class Call(tuple):
  """An operation that calls a procedure by label, storing the result in a
  destination variable"""

  def __new__(cls, dst, label):
    return tuple.__new__(cls, (dst, label))

  def __repr__(self):
    return "%s(dst=%r, label=%r)" % (type(self).__name__, self.dst, self.label)

  dst = property(lambda self: self[0])
  label = property(lambda self: self[1])

class Add(tuple):
  """An operation that adds two source variables, storing the result in a
  destination variable"""

  def __new__(cls, dst, srca, srcb):
    return tuple.__new__(cls, (dst, srca, srcb))

  def __repr__(self):
    return ("%s(dst=%r, srca=%r, srcb=%r)" % (type(self).__name__, self.dst,
      self.srca, self.srcb))

  dst = property(lambda self: self[0])
  srca = property(lambda self: self[1])
  srcb = property(lambda self: self[2])

class Jump(tuple):
  """An operation that jumps to the given label"""

  def __new__(cls, label):
    return tuple.__new__(cls, (label,))

  def __repr__(self):
    return "%s(label=%r)" % (type(self).__name__, self.label)

  label = property(lambda self: self[0])

class IfZeroJump(tuple):
  """An operation that jumps to the given label if the source variable is
  zero"""

  def __new__(cls, src, label):
    return tuple.__new__(cls, (src, label))

  def __repr__(self):
    return ("%s(src=%r, label=%r)" % (type(self).__name__, self.src,
      self.label))

  src = property(lambda self: self[0])
  label = property(lambda self: self[1])
