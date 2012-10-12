"""
Three-address code instructions and helper classes
"""

class AutoGen(object):
  """An automatic object generator"""
  def __init__(self, cls):
    self.cls = cls
    self.n = 0

  def next(self):
    n = self.n
    self.n += 1
    return self.cls(n)

class AutoVar(object):
  """An automatic variable generator"""
  def __init__(self, id):
    self.id = id

  def __repr__(self):
    return "AutoVar(id=%r)" % self.id

class AutoLabel(object):
  """An automatic label generator"""
  def __init__(self, id):
    self.id = id

  def __repr__(self):
    return "AutoLabel(id=%r)" % self.id

class Assign(object):
  """An assignment of a source constant or variable to a destination
  variable"""
  def __init__(self, dst, src):
    self.dst = dst
    self.src = src

  def __repr__(self):
    return "Assign(dst=%r, src=%r)" % (self.dst, self.src)

class PushParam(object):
  """An operation that pushes a variable onto the parameter stack for a future
  function call"""
  def __init__(self, src):
    self.src = src

  def __repr__(self):
    return "PushParam(src=%r)" % self.src

class PopParams(object):
  """An operation that removes words from the parameter stack"""
  def __init__(self, num):
    self.num = num

  def __repr__(self):
    return "PopParams(num=%r)" % self.num

class Call(object):
  """A function call whose result is stored in a destination variable"""
  def __init__(self, dst, proc):
    self.dst = dst
    self.proc = proc

  def __repr__(self):
    return "Call(dst=%r, proc=%r)" % (self.dst, self.proc)

class Add(object):
  """An operation that adds two source variable, storing the result in a
  destination variable"""
  def __init__(self, dst, srca, srcb):
    self.dst = dst
    self.srca = srca
    self.srcb = srcb

  def __repr__(self):
    return "Add(dst=%r, srca=%r, srcb=%r)" % (self.dst, self.srca, self.srcb)

class Return(object):
  """An operation that sets the return value of a function"""
  def __init__(self, src):
    self.src = src

  def __repr__(self):
    return "Return(src=%r)" % self.src

class Label(object):
  """A named jump target"""
  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return "Label(name=%r)" % self.name

class Goto(object):
  """An operation that jumps to the given label"""
  def __init__(self, label):
    self.label = label

  def __repr__(self):
    return "Goto(label=%r)" % self.label

class IfZeroGoto(object):
  """An operation that jumps to the given label if the test variable is
  zero"""
  def __init__(self, test, label):
    self.test = test
    self.label = label

  def __repr__(self):
    return "IfZeroGoto(test=%r, label=%r)" % (self.test, self.label)

class BeginFunc(object):
  """The beginning of a function, specifying the amount of local variable
  storage that should be reserved"""
  def __init__(self, nlocals=0):
    self.nlocals = nlocals

  def __repr__(self):
    return "BeginFunc(localc=%r)" % self.nlocals

class EndFunc(object):
  """The end of a function"""
  def __repr__(self):
    return "EndFunc()"
