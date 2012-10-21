"""
Virtual machine classes for encoding, decoding, and executing bytecode
"""

class InstructionError(Exception):
  """An error encountered while decoding an instruction"""

class ProcessorError(Exception):
  """An error encountered while accessing the processor"""

  def __init__(self, addr, message):
    Exception.__init__(self, message)
    self.addr = addr

  def __str__(self):
    return "address %04X: %s" % (self.addr, self.message)

class Operand(object):
  """An instruction operand"""

  # Operand addressing modes
  OPSPEC_MODE_IND = 0o10
  OPSPEC_MODE_OFF = 0o20
  OPSPEC_MODE_IND_OFF = 0o30
  OPSPEC_MODE_IND_INC = 0o40
  OPSPEC_MODE_IND_DEC = 0o50
  OPSPEC_MODE_SHORT_IMM = 0o60

  # A reserved register index that indicates an immediate value
  OPSPEC_REG_IMM = 0o7

  # Bit masks
  OPSPEC_MODE_MASK = 0o70
  OPSPEC_REG_MASK = 0o7
  OPSPEC_SHORT_IMM_BITS = 4
  OPSPEC_SHORT_IMM_MASK = 2**OPSPEC_SHORT_IMM_BITS - 1
  OPSPEC_SHORT_IMM_SIGN_MASK = 2**(OPSPEC_SHORT_IMM_BITS - 1)

  @classmethod
  def _decodeReg(cls, opspec):
    """Decode a register specification."""
    return opspec & cls.OPSPEC_REG_MASK

  @classmethod
  def _decodeShortImm(cls, opspec):
    """Decode a signed, short-form immediate value."""
    imm = opspec & cls.OPSPEC_SHORT_IMM_MASK

    # Sign-extend if necessary
    if imm & cls.OPSPEC_SHORT_IMM_SIGN_MASK:
      imm = ((imm * -1) & cls.OPSPEC_SHORT_IMM_MASK) * -1

    return imm

  @classmethod
  def decode(cls, opspec, seq):
    """Decode an operand, returning an operand instance."""
    if opspec >= 0o00 and opspec <= 0o06:
      return RegOperand(cls._decodeReg(opspec))
    elif opspec == 0o07:
      return ImmOperand(seq.next())
    elif opspec >= 0o10 and opspec <= 0o16:
      return IndRegOperand(cls._decodeReg(opspec))
    elif opspec == 0o17:
      return IndImmOperand(seq.next())
    elif opspec >= 0o20 and opspec <= 0o26:
      return RegOffOperand(cls._decodeReg(opspec), seq.next())
    elif opspec >= 0o30 and opspec <= 0o36:
      return IndRegOffOperand(cls._decodeReg(opspec), seq.next())
    elif opspec >= 0o40 and opspec <= 0o46:
      return IndIncRegOperand(cls._decodeReg(opspec))
    elif opspec >= 0o50 and opspec <= 0o56:
      return IndDecRegOperand(cls._decodeReg(opspec))
    elif opspec >= 0o60 and opspec <= 0o77:
      return ShortImmOperand(cls._decodeShortImm(opspec))
    else:
      raise InstructionError("invalid operand")

class RegOperand(Operand):
  """A register operand"""

  def __init__(self, reg):
    super(RegOperand, self).__init__()
    self.reg = reg

  def __repr__(self):
    return "%s(reg=%r)" % (type(self).__name__, self.reg)

  def __str__(self):
    return Processor.REG_NAMES[self.reg]

  def encode(self):
    return (self.reg, None)

  def modify(self, proc, f):
    proc.setReg(self.reg, f(proc.getReg(self.reg)))

class ImmOperand(Operand):
  """An immediate operand"""

  def __init__(self, val):
    super(ImmOperand, self).__init__()
    self.val = val

  def __repr__(self):
    return "%s(val=%r)" % (type(self).__name__, self.val)

  def __str__(self):
    return "%X" % self.val

  def encode(self):
    return (self.OPSPEC_REG_IMM, self.val)

  def modify(self, proc, f):
    f(self.val)

class RegOffOperand(RegOperand, ImmOperand):
  """A register + immediate offset operand"""

  def __init__(self, reg, val):
    # XXX Find a better way to handle __init__
    Operand.__init__(self)
    self.reg = reg
    self.val = val

  def __repr__(self):
    return "%s(reg=%r, val=%r)" % (self.reg, self.val)

  def __str__(self):
    return "%s + %s" % (RegOperand.__str__(self), ImmOperand.__str__(self))

  def encode(self):
    return (self.reg | self.OPSPEC_MODE_OFF, self.val)

  def modify(self, proc, f):
    def g(r):
      ImmOperand.modify(self, proc, lambda i: f((r + i) & Processor.WORD_MASK))
      return r

    RegOperand.modify(self, proc, g)

class IncRegOperand(RegOperand):
  """A register post-increment operand"""

  def __str__(self):
    return "%s++" % super(IncRegOperand, self).__str__()

  def modify(self, proc, f):
    def g(addr):
      f(addr)
      return (addr + 1) & Processor.WORD_MASK

    super(IncRegOperand, self).modify(proc, g)

class DecRegOperand(RegOperand):
  """A register pre-decrement operand"""

  def __str__(self):
    return "--%s" % super(DecRegOperand, self).__str__()

  def modify(self, proc, f):
    def g(addr):
      addr = (addr - 1) & Processor.WORD_MASK
      f(addr)
      return addr

    super(DecRegOperand, self).modify(proc, g)

class IndOperand(Operand):
  """An indirect operand"""

  def __str__(self):
    return "[%s]" % super(IndOperand, self).__str__()

  def encode(self):
    opspec, word = super(IndOperand, self).encode()
    return (opspec | self.OPSPEC_MODE_IND, word)

  def modify(self, proc, f):
    def g(addr):
      proc.setMem(addr, f(proc.getMem(addr)))
      return addr

    super(IndOperand, self).modify(proc, g)

class IndRegOperand(IndOperand, RegOperand):
  """An indirect register operand"""

class IndImmOperand(IndOperand, ImmOperand):
  """An indirect immediate operand"""

class IndRegOffOperand(IndOperand, RegOffOperand):
  """An indirect register + immediate offset operand"""

class IndIncRegOperand(IndOperand, IncRegOperand):
  """An indirect register post-increment operand"""

  def encode(self):
    opspec, word = super(IndIncRegOperand, self).encode()
    return ((opspec & ~self.OPSPEC_MODE_MASK)
              | self.OPSPEC_MODE_IND_INC, word)

class IndDecRegOperand(IndOperand, DecRegOperand):
  """An indirect register pre-decrement operand"""

  def encode(self):
    opspec, word = super(IndDecRegOperand, self).encode()
    return ((opspec & ~self.OPSPEC_MODE_MASK)
              | self.OPSPEC_MODE_IND_DEC, word)

class ShortImmOperand(Operand):
  """A short-form immediate operand"""

  def __init__(self, val):
    super(ShortImmOperand, self).__init__()

    if (val < -2**(self.OPSPEC_SHORT_IMM_BITS - 1)
      or val >= 2**(self.OPSPEC_SHORT_IMM_BITS - 1)):
      raise InstructionError("short-form immediate value out of range")

    self.val = val

  def __str__(self):
    return "$%X" % self.val

  def encode(self):
    return ((self.val & self.OPSPEC_SHORT_IMM_MASK)
              | self.OPSPEC_MODE_SHORT_IMM, None)

  def modify(self, proc, f):
    f(self.val)

class Instruction(object):
  """The base class for all instructions"""

  # Dictionaries for decoding/assembly
  _opcodes = {}
  _mnemonics = {}

  @classmethod
  def _operator(cls, opcode, mnemonic):
    """A decorator for defining operator classes"""
    mnemonic = mnemonic.upper()

    def decorator(opcls):
      opcls._opcode = opcode
      opcls._mnemonic = mnemonic

      cls._opcodes[opcode] = opcls
      cls._mnemonics[mnemonic] = opcls

      return opcls

    return decorator

  @classmethod
  def fromopcode(cls, opcode):
    """Return an instruction type for the given opcode."""
    return cls._opcodes[opcode]

  @classmethod
  def frommnemonic(cls, mnemonic):
    """Return an instruction type for the given mnemonic."""
    return cls._mnemonics[mnemonic.upper()]

  @staticmethod
  def setFlags(proc, val):
    """Set the flags register for the result of an operation."""
    flags = 0

    if not val:
      flags |= Processor.FLAG_ZERO

    proc.setReg(Processor.REG_FL, flags)

  @classmethod
  def decode(cls, seq):
    """Decode an instruction, returning an instruction instance."""
    inst = seq.next()

    opcode = inst >> 12
    try:
      opcls = cls.fromopcode(opcode)
    except KeyError:
      raise InstructionError("invalid opcode")
    opa = Operand.decode((inst >> 6) & 0o77, seq)
    opb = Operand.decode(inst & 0o77, seq)

    return opcls(opa, opb)

  def __init__(self, opa, opb):
    self.opa = opa
    self.opb = opb

  def __repr__(self):
    return "%s(opa=%r, opb=%r)" % (type(self).__name__, self.opa, self.opb)

  def __str__(self):
    return "%s %s, %s" % (self._mnemonic, str(self.opa), str(self.opb))

  def encode(self):
    """Encode an instruction, returning a list of words."""
    opspeca, aword = self.opa.encode()
    opspecb, bword = self.opb.encode()

    inst = (self._opcode << 12) | (opspeca << 6) | opspecb

    seq = [inst]
    if aword != None:
      seq.append(aword)
    if bword != None:
      seq.append(bword)

    return seq

  def _withOps(self, proc, f):
    """Modify this instruction's operands with the given function."""
    def g(a):
      g.a = a

      def h(b):
        g.a, b = f(g.a, b)
        return b

      self.opb.modify(proc, h)
      return g.a

    self.opa.modify(proc, g)

# Instruction implementations
@Instruction._operator(0x1, "SET")
class Set(Instruction):
  def execute(self, proc):
    self._withOps(proc, lambda a, b: (b, b))

@Instruction._operator(0x2, "IF")
class If(Instruction):
  def execute(self, proc):
    def f(a, b):
      if not (a & b):
        proc.skip()

      return (a, b)

    self._withOps(proc, f)

@Instruction._operator(0x4, "ADD")
class Add(Instruction):
  def execute(self, proc):
    def f(a, b):
      a = (a + b) & proc.WORD_MASK
      self.setFlags(proc, a)
      return (a, b)

    self._withOps(proc, f)

@Instruction._operator(0x5, "SUB")
class Sub(Instruction):
  def execute(self, proc):
    def f(a, b):
      a = (a - b) & proc.WORD_MASK
      self.setFlags(proc, a)
      return (a, b)

    self._withOps(proc, f)

@Instruction._operator(0x6, "MUL")
class Mul(Instruction):
  def execute(self, proc):
    def f(a, b):
      c = a * b
      a = c & proc.WORD_MASK
      b = c >> proc.WORD_BITS
      self.setFlags(proc, c)
      return (a, b)

    self._withOps(proc, f)

@Instruction._operator(0x7, "DIV")
class Div(Instruction):
  def execute(self, proc):
    def f(a, b):
      a /= b
      self.setFlags(proc, a)
      return (a, b)

    self._withOps(proc, f)

@Instruction._operator(0x8, "AND")
class And(Instruction):
  def execute(self, proc):
    def f(a, b):
      a &= b
      self.setFlags(proc, a)
      return (a, b)

    self._withOps(proc, f)

@Instruction._operator(0x9, "OR")
class Or(Instruction):
  def execute(self, proc):
    def f(a, b):
      a |= b
      self.setFlags(proc, a)
      return (a, b)

    self._withOps(proc, f)

@Instruction._operator(0xA, "XOR")
class Xor(Instruction):
  def execute(self, proc):
    def f(a, b):
      a ^= b
      self.setFlags(proc, a)
      return (a, b)

    self._withOps(proc, f)

def _regConstants(cls):
  """A helper for initializing register constants"""
  for i, n in enumerate(cls.REG_NAMES):
    setattr(cls, "REG_%s" % n, i)

  return cls

@_regConstants
class Processor(object):
  """A bytecode processor"""

  # Static parameters
  WORD_BITS = 16
  WORD_MASK = 2**WORD_BITS - 1

  # Register names (REG_* constants are initialized by _regConstants)
  REG_NAMES = ["X0", "X1", "X2", "X3", "FL", "SP", "IP"]

  # Flag bits
  FLAG_ZERO = 2**0

  def __init__(self, memWords):
    """Initialize the memory array and set the processor to a known state."""
    # Set up the memory
    assert memWords >= 0 and memWords <= 2**self.WORD_BITS
    self.memWords = memWords
    self.__mem = [0] * memWords

    # Set up the registers
    self.__regs = [0] * len(self.REG_NAMES)
    self.setReg(self.REG_SP, memWords)

    self.cycle = 0

  @classmethod
  def _checkWord(cls, val):
    """Check whether a word value is valid."""
    assert val >= 0 and val < 2**cls.WORD_BITS

  def _checkAddr(self, addr):
    """Check whether a memory address is valid."""
    self._checkWord(addr)
    if addr < 0 or addr >= self.memWords:
      raise ProcessorError(addr, "memory address out of range")

  def getMem(self, addr):
    """Get the value at the given memory location."""
    self._checkAddr(addr)
    return self.__mem[addr]

  def setMem(self, addr, val):
    """Set the value at the given memory location."""
    self._checkAddr(addr)
    self._checkWord(val)
    self.__mem[addr] = val

  def memSeq(self, addr):
    """A sequence of memory words starting from the given address."""
    while True:
      self._checkAddr(addr)
      yield self.getMem(addr)
      addr = (addr + 1) & self.WORD_MASK

  @classmethod
  def _checkReg(cls, reg):
    """Check whether a register index is valid."""
    assert reg >= 0 and reg < len(cls.REG_NAMES)

  def getReg(self, reg):
    """Get the value of a register."""
    self._checkReg(reg)
    return self.__regs[reg]

  def setReg(self, reg, val):
    """Set the value of a register."""
    self._checkReg(reg)
    self._checkWord(val)
    self.__regs[reg] = val

  def __iter__(self):
    """Return this instance as an iterator on the current instruction."""
    return self

  def next(self):
    """Return the word at the current instruction pointer, incrementing the
    instruction pointer."""
    ip = self.getReg(self.REG_IP)
    val = self.getMem(ip)
    self.setReg(self.REG_IP, (ip + 1) & self.WORD_MASK)
    return val

  def _decode(self):
    """Decode the next instruction."""
    try:
      ip = self.getReg(self.REG_IP)
      return Instruction.decode(self)
    except InstructionError, e:
      raise ProcessorError(ip, "error decoding instruction: %s" % e)

  def step(self):
    """Execute the instruction at the current instruction pointer."""
    try:
      ip = self.getReg(self.REG_IP)
      self._decode().execute(self)
    except ProcessorError:
      self.setReg(self.REG_IP, ip)
      raise
    self.cycle += 1

  def skip(self):
    """Skip the instruction at the current instruction pointer."""
    self._decode()
