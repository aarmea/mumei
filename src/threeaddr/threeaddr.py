"""
Three-address code instructions and helper classes
"""

# Helper classes

class AutoGen(object):
  """An automatic identifier generator that generates strings with the given
  prefix and passes them to the supplied function `f`, returning the result.
  """

  def __init__(self, prefix, f=id):
    self.prefix = prefix
    self.f = f
    self.n = 0

  def __iter__(self):
    return self

  def next(self):
    n = self.n
    self.n += 1
    return self.f("%s%d" % (self.prefix, self.n))

class ParamVar(tuple):
  """A parameter variable"""

  def __new__(cls, off):
    return tuple.__new__(cls, (off,))

  def __repr__(self):
    return "%s(off=%r)" % (type(self).__name__, self.off)

  off = property(lambda self: self[0])
  """The offset of the parameter"""

class LocalVar(tuple):
  """A local variable"""

  def __new__(cls, id_):
    return tuple.__new__(cls, (id_,))

  def __repr__(self):
    return "%s(id_=%r)" % (type(self).__name__, self.id)

  id = property(lambda self: self[0])
  """The name of the variable"""

class GlobalVar(tuple):
  """A global variable"""

  def __new__(cls, id_):
    return tuple.__new__(cls, (id_,))

  def __repr__(self):
    return "%s(id_=%r)" % (type(self).__name__, self.id)

  id = property(lambda self: self[0])
  """The name of the variable"""

# Three-address code instructions and directives

class Label(tuple):
  """A named jump target"""

  def __new__(cls, id_):
    return tuple.__new__(cls, (id_,))

  def __repr__(self):
    return "%s(id_=%r)" % (type(self).__name__, self.id)

  id = property(lambda self: self[0])
  """The name of the jump target"""

class Word(tuple):
  """A literal word"""

  def __new__(cls, val):
    return tuple.__new__(cls, (val,))

  def __repr__(self):
    return "%s(val=%r)" % (type(self).__name__, self.val)

  val = property(lambda self: self[0])
  """The value of the word"""

class BeginFunc(tuple):
  """Begin a function, allocating the given number of words on the stack for
  local variables"""

  def __new__(cls, nwords):
    return tuple.__new__(cls, (nwords,))

  def __repr__(self):
    return "%s(nwords=%r)" % (type(self).__name__, self.nwords)

  nwords = property(lambda self: self[0])
  """The number of stack words to reserve for local variables"""

class EndFunc(tuple):
  """End a function, using the given variable as the return value"""

  def __new__(cls, ret):
    return tuple.__new__(cls, (ret,))

  def __repr__(self):
    return "%s(ret=%r)" % (type(self).__name__, self.ret)

  ret = property(lambda self: self[0])
  """The return value"""

class Assign(tuple):
  """An operation that assigns the source to the destination"""

  def __new__(cls, dst, src):
    return tuple.__new__(cls, (dst, src))

  def __repr__(self):
    return "%s(dst=%r, src=%r)" % (type(self).__name__, self.dst, self.src)

  dst = property(lambda self: self[0])
  """The destination operand"""

  src = property(lambda self: self[1])
  """The source operand"""

class AddressOf(tuple):
  """An operation that assigns the address of the source to the destination"""

  def __new__(cls, dst, src):
    return tuple.__new__(cls, (dst, src))

  def __repr__(self):
    return "%s(dst=%r, src=%r)" % (type(self).__name__, self.dst, self.src)

  dst = property(lambda self: self[0])
  """The destination operand"""

  src = property(lambda self: self[1])
  """The source operand"""

class Load(tuple):
  """An operation that copies the value at the source address to the
  destination"""

  def __new__(cls, dst, src):
    return tuple.__new__(cls, (dst, src))

  def __repr__(self):
    return "%s(dst=%r, src=%r)" % (type(self).__name__, self.dst, self.src)

  dst = property(lambda self: self[0])
  """The destination operand"""

  src = property(lambda self: self[1])
  """The source address"""

class Store(tuple):
  """An operation that copies the source to the destination address"""

  def __new__(cls, dst, src):
    return tuple.__new__(cls, (dst, src))

  def __repr__(self):
    return "%s(dst=%r, src=%r)" % (type(self).__name__, self.dst, self.src)

  dst = property(lambda self: self[0])
  """The destination address"""

  src = property(lambda self: self[1])
  """The source operand"""

class PushParam(tuple):
  """An operation that pushes the source onto the parameter stack for a future
  function call"""

  def __new__(cls, src):
    return tuple.__new__(cls, (src,))

  def __repr__(self):
    return "%s(src=%r)" % (type(self).__name__, self.src)

  src = property(lambda self: self[0])
  """The source operand"""

class PopParams(tuple):
  """An operation that removes words from the parameter stack"""

  def __new__(cls, nwords):
    return tuple.__new__(cls, (nwords,))

  def __repr__(self):
    return "%s(nwords=%r)" % (type(self).__name__, self.nwords)

  nwords = property(lambda self: self[0])
  """The number of words to remove"""

class Call(tuple):
  """An operation that calls a procedure at the target address, storing the
  result in the destination"""

  def __new__(cls, dst, target):
    return tuple.__new__(cls, (dst, target))

  def __repr__(self):
    return ("%s(dst=%r, target=%r)" % (type(self).__name__, self.dst,
      self.target))

  dst = property(lambda self: self[0])
  """The destination operand"""

  target = property(lambda self: self[1])
  """The address of the procedure to call"""

class LessThan(tuple):
  """An operation that sets the result to non-zero if the first operand is less
  than the second, otherwise zero."""

  def __new__(cls, dst, srca, srcb):
    return tuple.__new__(cls, (dst, srca, srcb))

  def __repr__(self):
    return ("%s(dst=%r, srca=%r, srcb=%r)" % (type(self).__name__, self.dst,
      self.srca, self.srcb))

  dst = property(lambda self: self[0])
  """The destination operand"""

  srca = property(lambda self: self[1])
  """The first source operand"""

  srcb = property(lambda self: self[2])
  """The second source operand"""

class BinOp(tuple):
  """An operation on two source operands that stores the result in the
  destination"""

  def __new__(cls, dst, srca, srcb):
    return tuple.__new__(cls, (dst, srca, srcb))

  def __repr__(self):
    return ("%s(dst=%r, srca=%r, srcb=%r)" % (type(self).__name__, self.dst,
      self.srca, self.srcb))

  dst = property(lambda self: self[0])
  """The destination operand"""

  srca = property(lambda self: self[1])
  """The first source operand"""

  srcb = property(lambda self: self[2])
  """The second source operand"""

class And(BinOp):
  """An operation that takes the bitwise AND of two source operands, storing the
  result in the destination"""

class Add(BinOp):
  """An operation that adds two source operands, storing the result in the
  destination"""

class Sub(BinOp):
  """An operation that subtracts two source operands, storing the result in
  the destination"""

class Jump(tuple):
  """An operation that jumps to the given target"""

  def __new__(cls, target):
    return tuple.__new__(cls, (target,))

  def __repr__(self):
    return "%s(target=%r)" % (type(self).__name__, self.target)

  target = property(lambda self: self[0])
  """The address of the jump target"""

class IfZeroJump(tuple):
  """An operation that jumps to the target address if the source operand is
  zero"""

  def __new__(cls, src, target):
    return tuple.__new__(cls, (src, target))

  def __repr__(self):
    return ("%s(src=%r, target=%r)" % (type(self).__name__, self.src,
      self.target))

  src = property(lambda self: self[0])
  """The source operand"""

  target = property(lambda self: self[1])
  """The address of the jump target"""
