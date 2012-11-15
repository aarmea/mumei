"""
A scanner for ANSI C
"""

import new
import string

import error

# General types
class Position(tuple):
  """The position of a token or error in an input string"""

  def __new__(cls, line, col):
    return tuple.__new__(cls, (line, col))

  def __repr__(self):
    return "%s(line=%r, col=%r)" % (type(self).__name__, self.line, self.col)

  def __str__(self):
    return "line %d, column %d" % (self.line, self.col)

  def next(self, c='\0'):
    """Return the next position after consuming the given character."""
    if c == '\n':
      return Position(self.line + 1, 1)
    else:
      return Position(self.line, self.col + 1)

  line = property(lambda self: self[0])
  col = property(lambda self: self[1])

class ScanError(error.CompileError):
  """An error encountered while scanning a string"""

class ScanWarning(error.CompileWarning):
  """A warning raised while scanning a string"""

# Token types
class Token(tuple):
  """The base class of all tokens"""

  def __new__(cls, pos):
    return tuple.__new__(cls, (pos,))

  def __repr__(self):
    return "%s(pos=%r)" % (type(self).__name__, self.pos)

  pos = property(lambda self: self[0])
  """The position of the token in the input string"""

class ValueToken(Token):
  """The base class of all tokens with a value"""

  def __new__(cls, pos, val):
    return tuple.__new__(cls, (pos, val))

  def __repr__(self):
    return "%s(pos=%r, val=%r)" % (type(self).__name__, self.pos, self.val)

  val = property(lambda self: self[1])
  """The value associated with the token"""

class IdentifierToken(ValueToken):
  """An identifier token"""

  def __str__(self):
    return "identifier"

class KeywordToken(ValueToken):
  """A keyword token"""

  def __str__(self):
    return "`%s' keyword" % self.val

class IntToken(ValueToken):
  """An integer constant token"""

  def __str__(self):
    return "int constant"

class LongToken(ValueToken):
  """A long integer constant token"""

  def __str__(self):
    return "long constant"

class UIntToken(ValueToken):
  """An unsigned integer constant token"""

  def __str__(self):
    return "unsigned int constant"

class ULongToken(ValueToken):
  """A unsigned long integer constant token"""

  def __str__(self):
    return "unsigned long constant"

class FloatToken(ValueToken):
  """A floating-point constant token"""

  def __str__(self):
    return "float constant"

class DoubleToken(ValueToken):
  """A double constant token"""

  def __str__(self):
    return "double constant"

class LongDoubleToken(ValueToken):
  """A long double constant value"""

  def __str__(self):
    return "long double constant"

class CharToken(ValueToken):
  """A character constant token"""

  def __str__(self):
    return "character constant"

class WCharToken(ValueToken):
  """A wide character constant token"""

  def __str__(self):
    return "wide character constant"

class StringToken(ValueToken):
  """A string literal token"""

  def __str__(self):
    return "string literal"

class WStringToken(ValueToken):
  """A wide-string literal token"""

  def __str__(self):
    return "wide-string literal"

class EllipsisToken(Token):
  """An ellipsis token"""

  def __str__(self):
    return "..."

class RightShiftAssignToken(Token):
  """A right shift assignment token"""

  def __str__(self):
    return ">>="

class LeftShiftAssignToken(Token):
  """A left shift assignment token"""

  def __str__(self):
    return "<<="

class AddAssignToken(Token):
  """An addition assignment token"""

  def __str__(self):
    return "+="

class SubAssignToken(Token):
  """A subtraction assignment token"""

  def __str__(self):
    return "-="

class MulAssignToken(Token):
  """A multiplication assignment token"""

  def __str__(self):
    return "*="

class DivAssignToken(Token):
  """A division assignment token"""

  def __str__(self):
    return "/="

class ModAssignToken(Token):
  """A modulo assignment token"""

  def __str__(self):
    return "%="

class AndAssignToken(Token):
  """A bitwise AND assignment token"""

  def __str__(self):
    return "&="

class XorAssignToken(Token):
  """A bitwise exclusive OR assignment token"""

  def __str__(self):
    return "^="

class OrAssignToken(Token):
  """A bitwise OR assignment token"""

  def __str__(self):
    return "|="

class RightShiftToken(Token):
  """A right shift token"""

  def __str__(self):
    return ">>"

class LeftShiftToken(Token):
  """A left shift token"""

  def __str__(self):
    return "<<"

class IncrementToken(Token):
  """An increment token"""

  def __str__(self):
    return "++"

class DecrementToken(Token):
  """A decrement token"""

  def __str__(self):
    return "--"

class ArrowToken(Token):
  """An arrow token"""

  def __str__(self):
    return "->"

class LogicAndToken(Token):
  """A logical AND token"""

  def __str__(self):
    return "&&"

class LogicOrToken(Token):
  """A logical OR token"""

  def __str__(self):
    return "||"

class GreaterThanEqualToken(Token):
  """A greater-than-or-equal-to token"""

  def __str__(self):
    return ">="

class LessThanEqualToken(Token):
  """A less-than-or-equal-to token"""

  def __str__(self):
    return "<="

class EqualToken(Token):
  """An equal-to token"""

  def __str__(self):
    return "=="

class NotEqualToken(Token):
  """A not-equal-to token"""

  def __str__(self):
    return "!="

class SemicolonToken(Token):
  """A semicolon token"""

  def __str__(self):
    return ";"

class LCurlyToken(Token):
  """A left curly bracket token"""

  def __str__(self):
    return "{"

class RCurlyToken(Token):
  """A right curly bracket token"""

  def __str__(self):
    return "}"

class CommaToken(Token):
  """A comma token"""

  def __str__(self):
    return ","

class ColonToken(Token):
  """A colon token"""

  def __str__(self):
    return ":"

class AssignToken(Token):
  """An assignment token"""

  def __str__(self):
    return "="

class LParenToken(Token):
  """A left parenthesis token"""

  def __str__(self):
    return "("

class RParenToken(Token):
  """A right parenthesis token"""

  def __str__(self):
    return ")"

class LSquareToken(Token):
  """A left square bracket token"""

  def __str__(self):
    return "["

class RSquareToken(Token):
  """A right square bracket token"""

  def __str__(self):
    return "]"

class PeriodToken(Token):
  """A period token"""

  def __str__(self):
    return "."

class AddToken(Token):
  """An addition token"""

  def __str__(self):
    return "+"

class SubToken(Token):
  """A subtraction token"""

  def __str__(self):
    return "-"

class StarToken(Token):
  """A star token"""

  def __str__(self):
    return "*"

class DivToken(Token):
  """A division token"""

  def __str__(self):
    return "/"

class ModToken(Token):
  """A modulo token"""

  def __str__(self):
    return "%"

class LogicNotToken(Token):
  """A logical NOT token"""

  def __str__(self):
    return "!"

class NotToken(Token):
  """A bitwise NOT token"""

  def __str__(self):
    return "~"

class AmpersandToken(Token):
  """An ampersand token"""

  def __str__(self):
    return "&"

class XorToken(Token):
  """A bitwise exclusive OR token"""

  def __str__(self):
    return "^"

class OrToken(Token):
  """A bitwise OR token"""

  def __str__(self):
    return "|"

class GreaterThanToken(Token):
  """A greater-than token"""

  def __str__(self):
    return ">"

class LessThanToken(Token):
  """A less-than token"""

  def __str__(self):
    return "<"

class QuestionToken(Token):
  """A question mark token"""

  def __str__(self):
    return "?"

class EOFToken(Token):
  """An end-of-file token"""

  def __str__(self):
    return "end of file"

# Scanner types
class Scanner(object):
  """A base class for continuation- and state-based scanners

  Each state is a function that is passed the current character (or None at
  EOF), the current position, and continuations for transitioning to the given
  state and consuming the current character or passing it to the next state
  respectively.

  self._state is used as the starting state for scanners derived from this
  class. Scanners should transition to self._final to terminate.
  """

  def __init__(self, final=None):
    self._final = final

  def __call__(self, c, off, pos, cconsume, cpass):
    return self._start(c, off, pos, cconsume, cpass)

class ScannerIter(object):
  """An iterator that runs a scanner on an input and yields a sequence of
  tokens"""

  def __init__(self, start, str_, trace=False):
    self._state = start
    self.str = str_
    self.off = 0
    self.pos = Position(1, 1)
    self.trace = trace

  def __consume(self, newState, off, pos, toks):
    """Transition to a new state, emitting the given tokens and consuming the
    current character."""
    return (newState, off + 1, pos.next(self.c(off)), toks)

  def __pass(self, newState, curOff, curPos, curToks):
    """Transition to a new state, emitting the given tokens and passing the
    current character to that state."""
    if newState:
      if self.trace:
        if isinstance(newState, new.instancemethod):
          name = "%s.%s" % (newState.im_class.__name__, newState.__name__)
        elif isinstance(newState, new.function):
          name = newState.__name__
        else:
          name = "%s._start" % type(newState).__name__
        print "%s(%r)" % (name, self.c(curOff))

      return newState(self.c(curOff), curOff, curPos,
        lambda s, toks=(): self.__consume(s, curOff, curPos, curToks + toks),
        lambda s, off=curOff, pos=curPos, toks=():
          self.__pass(s, off, pos, curToks + toks))
    else:
      return (None, curOff, curPos, curToks)

  def __iter__(self):
    """Process the input, generating a sequence of tokens."""
    while self._state:
      self._state, self.off, self.pos, toks = self.__pass(self._state,
        self.off, self.pos, ())
      for tok in toks:
        yield tok

  def c(self, off):
    if off < len(self.str):
      return self.str[off]
    else:
      return None

  done = property(lambda self: self.off == len(self.str))

class IdentifierOrKeywordScanner(Scanner):
  """A scanner that accepts identifiers or keywords"""

  KEYWORDS = frozenset(["auto", "break", "case", "char", "const", "continue",
    "default", "do", "double", "else", "enum", "extern", "float", "for", "goto",
    "if", "int", "long", "register", "return", "short", "signed", "sizeof",
    "static", "struct", "switch", "typedef", "union", "unsigned", "void",
    "volatile", "while"])

  def __getTok(self):
    """Generate the appropriate token based on the consumed input."""
    if self.tokStr not in self.KEYWORDS:
      return IdentifierToken(self.tokPos, self.tokStr)
    else:
      return KeywordToken(self.tokPos, self.tokStr)

  def _start(self, c, off, pos, cconsume, cpass):
    """The starting state (no input)"""
    self.tokPos = pos
    self.tokStr = c

    if c and (c.isalpha() or c == '_'):
      return cconsume(self._identifier)
    else:
      # This scanner isn't called directly, so this shouldn't happen.
      assert False

  def _identifier(self, c, off, pos, cconsume, cpass):
    """The main character sequence"""
    if c and (c.isalnum() or c == '_'):
      self.tokStr += c
      return cconsume(self._identifier)
    else:
      return cpass(self._final, toks=(self.__getTok(),))

class NumberScanner(Scanner):
  """A scanner that accepts numeric constants

  Integer constants:
  0[xX][\da-fA-F]+([uU][lL]?|[lL]?[uU]?) (hex)
  0[0-7]*([uU][lL]?|[lL]?[uU]?) (octal)
  \d+([uU][lL]?|[lL]?[uU]?) (decimal)

  Floating-point constants:
  \d+[eE][+-]?\d+[fFlL]?
  \d*\.\d+([eE][+-]?\d+)?[fFlL]?
  \d+\.([eE][+-]?\d+)?[fFlL]?
  """

  BASE_DIGITS = {8: string.octdigits, 10: string.digits, 16: string.hexdigits}

  def _isDigit(self, c):
    """Return whether the given character is a valid digit in the current
    base."""
    return c in self.BASE_DIGITS[self.base]

  def _start(self, c, off, pos, cconsume, cpass):
    """The starting state (no input)"""
    self.tokPos = pos
    self.tokStr = ""
    self.base = 10
    self.hasU = False
    self.hasL = False
    self.hasF = False

    if c and c == '0':
      self.tokStr += c
      return cconsume(self._hexOrOctal)
    elif c.isdigit() or c == '.':
      return cpass(self._digits)
    else:
      # This scanner isn't called directly, so this shouldn't happen.
      assert False

  def _hexOrOctal(self, c, off, pos, cconsume, cpass):
    """A single zero has been read"""
    if c and c in "xX":
      self.base = 16
      return cconsume(self._digits)
    else:
      self.base = 8
      self.octPos = None
      return cpass(self._digits)

  def _digits(self, c, off, pos, cconsume, cpass):
    """The main sequence of digits"""
    if c and self._isDigit(c):
      self.tokStr += c
      return cconsume(self._digits)
    elif c and c.isdigit():
      self.tokStr += c
      # Defer raising an error until we know this isn't a floating-point
      # constant beginning with 0.
      self.octPos = pos
      self.octDigit = c
      return cconsume(self._digits)
    elif c and c == '.':
      self.tokStr += c
      return cconsume(self._decimal)
    elif c and c in "eE":
      self.tokStr += c
      return cconsume(self._exponent)
    elif c and c in "fF":
      return cpass(self._floatSuffix)
    else:
      # Raise an error if this is an octal constant with non-octal digits.
      if self.base == 8 and self.octPos:
        raise ScanError(self.octPos, "invalid digit `%s' in octal constant" %
          self.octDigit)
      return cpass(self._intSuffix)

  def _intSuffix(self, c, off, pos, cconsume, cpass):
    """The end of an integer"""
    if c and not self.hasU and c in "uU":
      self.hasU = True
      return cconsume(self._intSuffix)
    elif c and not self.hasL and c in "lL":
      self.hasL = True
      return cconsume(self._intSuffix)
    elif c and c.isalnum():
      raise ScanError(pos, "invalid suffix `%s' on integer constant" % c)
    else:
      if self.hasU and self.hasL:
        cls = ULongToken
      elif self.hasU and not self.hasL:
        cls = UIntToken
      elif not self.hasU and self.hasL:
        cls = LongToken
      else:
        cls = IntToken
      val = int(self.tokStr, self.base)
      return cpass(self._final, toks=(cls(self.tokPos, val),))

  def _decimal(self, c, off, pos, cconsume, cpass):
    """In a floating-point number after the decimal point, if any"""
    if c and c.isdigit():
      self.tokStr += c
      return cconsume(self._decimal)
    elif c and c in "eE":
      self.tokStr += c
      return cconsume(self._exponent)
    else:
      return cpass(self._floatSuffix)

  def _exponent(self, c, off, pos, cconsume, cpass):
    """In an exponent immediately after the 'e'"""
    if c and c.isdigit():
      return cpass(self._exponentDigits)
    elif c and c in "+-":
      self.tokStr += c
    return cconsume(self._exponentSign)

  def _exponentSign(self, c, off, pos, cconsume, cpass):
    """In an exponent after the sign, if any"""
    if c and c.isdigit():
      return cpass(self._exponentDigits)
    else:
      raise ScanError(pos, "exponent has no digits")

  def _exponentDigits(self, c, off, pos, cconsume, cpass):
    """The main sequence of digits in an exponent"""
    if c and c.isdigit():
      self.tokStr += c
      return cconsume(self._exponentDigits)
    else:
      return cpass(self._floatSuffix)

  def _floatSuffix(self, c, off, pos, cconsume, cpass):
    """The end of a floating-point constant"""
    if c and not (self.hasF or self.hasL) and c in "fF":
      self.hasF = True
      return cconsume(self._floatSuffix)
    elif c and not (self.hasF or self.hasL) and c in "lL":
      self.hasL = True
      return cconsume(self._floatSuffix)
    elif c and c.isalnum():
      raise ScanError(pos, "invalid suffix `%s' on floating constant" % c)
    else:
      if self.hasF:
        cls = FloatToken
      elif self.hasL:
        cls = LongDoubleToken
      else:
        cls = DoubleToken
      val = float(self.tokStr)
      return cpass(self._final, toks=(cls(self.tokPos, val),))

class CharScanner(Scanner):
  """A scanner that accept character constants"""

  # Escape character mappings
  CHAR_ESCAPES = {'0': '\0', '\'': '\'', '"': '"', '?': '?', '\\': '\\',
    'a': '\a', 'b': '\b', 'f': '\f', 'n': '\n', 'r': '\r', 't': '\t',
    'v': '\v'}

  @classmethod
  def escapedChar(cls, c, pos):
    """Return the actual character value for an escaped character."""
    try:
      return cls.CHAR_ESCAPES[c]
    except KeyError:
      raise ScanError(pos, "unknown escape sequence: `\\%s'" % c)

  def _start(self, c, off, pos, cconsume, cpass):
    """The starting state"""
    self.tokPos = pos
    self.escape = False

    if c and c == 'L':
      self.wide = True
      return cconsume(self._open)
    else:
      self.wide = False
      return cpass(self._open)

  def _open(self, c, off, pos, cconsume, cpass):
    """Before an opening quote"""
    if c and c == '\'':
      return cconsume(self._char)
    else:
      # This scanner isn't called directly, so this shouldn't happen.
      assert False

  def _char(self, c, off, pos, cconsume, cpass):
    """The character constant"""
    if c:
      if self.escape:
        self.tokVal = CharScanner.escapedChar(c, pos)
      else:
        if c == '\\':
          self.escape = True
          return cconsume(self._char)
        else:
          self.tokVal = c
      return cconsume(self._close)
    else:
      return cpass(self._close)

  def _close(self, c, off, pos, cconsume, cpass):
    """Before a closing quote"""
    if c and c == '\'':
      if not self.wide:
        cls = CharToken
      else:
        cls = WCharToken
      return cconsume(self._final, (cls(self.tokPos, self.tokVal),))
    else:
      raise ScanError(pos, "missing terminating ' character")

class StringScanner(Scanner):
  """A scanner that accepts string literals"""

  def _start(self, c, off, pos, cconsume, cpass):
    """The starting state"""
    self.tokPos = pos
    self.tokStr = ""
    self.escape = False

    if c and c == 'L':
      self.wide = True
      return cconsume(self._open)
    else:
      self.wide = False
      return cpass(self._open)

  def _open(self, c, off, pos, cconsume, cpass):
    """Before an opening quote"""
    if c and c == '"':
      return cconsume(self._string)
    else:
      # This scanner isn't called directly, so this shouldn't happen.
      assert False

  def _string(self, c, off, pos, cconsume, cpass):
    """In a string literal"""
    if c:
      if self.escape:
        self.tokStr += CharScanner.escapedChar(c, pos)
        self.escape = False
      else:
        if c == '"':
          if not self.wide:
            cls = StringToken
          else:
            cls = WStringToken
          return cconsume(self._final, (cls(self.tokPos, self.tokStr),))
        else:
          if c == '\\':
            self.escape = True
          else:
            self.tokStr += c
      return cconsume(self._string)
    else:
      raise ScanError(pos, "unexpected EOF in string literal")

class CScanner(Scanner):
  """A scanner that generates C tokens from an input string"""

  @classmethod
  def _genPeriods(cls, pos, n):
    """Return (a tuple of n sequential period tokens starting at the given
    position, the next available position)."""
    if not n:
      return ((), pos)
    else:
      toks_, pos_ = cls._genPeriods(pos.next(), n - 1)
      return ((PeriodToken(pos),) + toks_, pos_)

  def _closeParen(self):
    """Consume a right parenthesis, updating the open parenthesis count."""
    self.openParens -= 1
    if self.openParens < 0:
      raise ScanError(self.tokPos, "unmatched `)'")

  def _closeCurly(self):
    """Consume a right curly bracket, updating the open curly bracket count."""
    self.openCurly -= 1
    if self.openCurly < 0:
      raise ScanError(self.tokPos, "unmatched `}'")

  def _closeSquare(self):
    """Consume a right square bracket, updating the open square bracket
    count."""
    self.openSquare -= 1
    if self.openSquare < 0:
      raise ScanError(self.tokPos, "unmatched `]'")

  def _start(self, c, off, pos, cconsume, cpass):
    """The starting state"""
    self.openParens = 0
    self.openCurly = 0
    self.openSquare = 0
    self.newline = True

    return cpass(self._main)

  def _main(self, c, off, pos, cconsume, cpass):
    """The main sequence of tokens"""
    self.tokOff = off
    self.tokPos = pos

    if c:
      self.newline = (c == '\n')

      if c.isalpha() or c == '_':
        if c == 'L':
          return cconsume(self._identifierOrWide)
        else:
          return cpass(IdentifierOrKeywordScanner(self._main))
      elif c.isdigit():
        return cpass(NumberScanner(self._main))
      elif c == '\'':
        return cpass(CharScanner(self._main))
      elif c == '"':
        return cpass(StringScanner(self._main))
      elif c == '.':
        return cconsume(self._dot)
      elif c == '>':
        return cconsume(self._greater)
      elif c == '<':
        return cconsume(self._less)
      elif c == '+':
        return cconsume(self._plus)
      elif c == '-':
        return cconsume(self._minus)
      elif c == '*':
        return cconsume(self._star)
      elif c == '/':
        return cconsume(self._slash)
      elif c == '%':
        return cconsume(self._percent)
      elif c == '&':
        return cconsume(self._amp)
      elif c == '^':
        return cconsume(self._caret)
      elif c == '|':
        return cconsume(self._pipe)
      elif c == '=':
        return cconsume(self._equal)
      elif c == '!':
        return cconsume(self._excl)
      elif c == ';':
        return cconsume(self._main, (SemicolonToken(pos),))
      elif c == '{':
        self.openCurly += 1
        return cconsume(self._main, (LCurlyToken(pos),))
      elif c == '}':
        self._closeCurly()
        return cconsume(self._main, (RCurlyToken(pos),))
      elif c == ',':
        return cconsume(self._main, (CommaToken(pos),))
      elif c == ':':
        return cconsume(self._colon)
      elif c == '(':
        self.openParens += 1
        return cconsume(self._main, (LParenToken(pos),))
      elif c == ')':
        self._closeParen()
        return cconsume(self._main, (RParenToken(pos),))
      elif c == '[':
        self.openSquare += 1
        return cconsume(self._main, (LSquareToken(pos),))
      elif c == ']':
        self._closeSquare()
        return cconsume(self._main, (RSquareToken(pos),))
      elif c == '?':
        return cconsume(self._main, (QuestionToken(pos),))
      elif c.isspace():
        return cconsume(self._main)
      else:
        raise ScanError(pos, "unrecognized character: `%s'" % c)
    else:
      if self.openParens > 0:
        raise ScanError(pos, "unexpected EOF: unmatched `('")
      if self.openCurly > 0:
        raise ScanError(pos, "unexpected EOF: unmatched `{'")
      if self.openSquare > 0:
        raise ScanError(pos, "unexpected EOF: unmatched `['")
      if not self.newline:
        toks = (ScanWarning(pos, "no newline at end of file"),)
      else:
        toks = ()
      return cpass(self._final, toks=toks + (EOFToken(pos),))

  def _identifierOrWide(self, c, off, pos, cconsume, cpass):
    """An 'L' has been read"""
    if c and c == '\'':
      return cpass(CharScanner(self._main), self.tokOff, self.tokPos)
    elif c and c == '"':
      return cpass(StringScanner(self._main), self.tokOff, self.tokPos)
    else:
      return cpass(IdentifierOrKeywordScanner(self._main), self.tokOff,
        self.tokPos)

  def _comment(self, c, off, pos, cconsume, cpass):
    """In a comment"""
    if c and c == '*':
      return cconsume(self._commentStar)
    elif c:
      return cconsume(self._comment)
    else:
      raise ScanError(pos, "unexpected EOF in comment")

  def _commentStar(self, c, off, pos, cconsume, cpass):
    """In a comment after an asterisk"""
    if c and c == '/': # End the comment
      return cconsume(self._main)
    else:
      return cpass(self._comment)

  def _dot(self, c, off, pos, cconsume, cpass):
    """One dot has been read"""
    if c and c == '.':
      return cconsume(self._2dot)
    elif c and c.isdigit():
      # A number beginning with a decimal point
      return cpass(NumberScanner(self._main), self.tokOff, self.tokPos)
    else:
      toks, pos_ = self._genPeriods(self.tokPos, 1)
      return cpass(self._main, toks=toks)

  def _2dot(self, c, off, pos, cconsume, cpass):
    """Two dots have been read"""
    if c and c == '.':
      return cconsume(self._3dot)
    elif c and c.isdigit():
      # Reserve a dot for the number
      toks, pos_ = self._genPeriods(self.tokPos, 1)
      return cpass(NumberScanner(self._main), self.tokOff + 1, pos_, toks=toks)
    else:
      toks, pos_ = self._genPeriods(self.tokPos, 2)
      return cpass(self._main, toks=toks)

  def _3dot(self, c, off, pos, cconsume, cpass):
    """Three dots have been read"""
    if c and c.isdigit():
      # Reserve a dot for the number
      toks, pos_ = self._genPeriods(self.tokPos, 2)
      return cpass(NumberScanner(self._main), self.tokOff + 2, pos_, toks=toks)
    else:
      return cpass(self._main, toks=(EllipsisToken(self.tokPos),))

  def _greater(self, c, off, pos, cconsume, cpass):
    """A greater-than symbol has been read"""
    if c and c == '>':
      return cconsume(self._2greater)
    elif c and c == '=':
      return cconsume(self._main, (GreaterThanEqualToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(GreaterThanToken(self.tokPos),))

  def _2greater(self, c, off, pos, cconsume, cpass):
    """Two greater-than symbols have been read"""
    if c and c == '=':
      return cconsume(self._main, (RightShiftAssignToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(RightShiftToken(self.tokPos),))

  def _less(self, c, off, pos, cconsume, cpass):
    """A less-than symbol has been read"""
    if c and c == '<':
      return cconsume(self._2less)
    elif c and c == '=':
      return cconsume(self._main, (LessThanEqualToken(self.tokPos),))
    elif c and c == '%': # Left curly bracket digraph
      self.openCurly += 1
      return cconsume(self._main, (LCurlyToken(self.tokPos),))
    elif c and c == ':': # Left square bracket digraph
      self.openSquare += 1
      return cconsume(self._main, (LSquareToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(LessThanToken(self.tokPos),))

  def _2less(self, c, off, pos, cconsume, cpass):
    """Two less-than symbols have been read"""
    if c and c == '=':
      return cconsume(self._main, (LeftShiftAssignToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(LeftShiftToken(self.tokPos),))

  def _plus(self, c, off, pos, cconsume, cpass):
    """A plus sign has been read"""
    if c and c == '=':
      return cconsume(self._main, (AddAssignToken(self.tokPos),))
    elif c and c == '+':
      return cconsume(self._main, (IncrementToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(AddToken(self.tokPos),))

  def _minus(self, c, off, pos, cconsume, cpass):
    """A minus sign has been read"""
    if c and c == '=':
      return cconsume(self._main, (SubAssignToken(self.tokPos),))
    elif c and c == '-':
      return cconsume(self._main, (DecrementToken(self.tokPos),))
    elif c and c == '>':
      return cconsume(self._main, (ArrowToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(SubToken(self.tokPos),))

  def _star(self, c, off, pos, cconsume, cpass):
    """A star has been read"""
    if c and c == '=':
      return cconsume(self._main, (MulAssignToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(StarToken(self.tokPos),))

  def _slash(self, c, off, pos, cconsume, cpass):
    """A slash has been read"""
    if c and c == '*': # Begin a comment
      return cconsume(self._comment)
    elif c and c == '=':
      return cconsume(self._main, (DivAssignToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(DivToken(self.tokPos),))

  def _percent(self, c, off, pos, cconsume, cpass):
    """A percent sign has been read"""
    if c and c == '=':
      return cconsume(self._main, (ModAssignToken(self.tokPos),))
    elif c and c == '>': # Right curly bracket digraph
      self._closeCurly()
      return cconsume(self._main, (RCurlyToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(ModToken(self.tokPos),))

  def _amp(self, c, off, pos, cconsume, cpass):
    """An ampersand has been read"""
    if c and c == '=':
      return cconsume(self._main, (AndAssignToken(self.tokPos),))
    elif c and c == '&':
      return cconsume(self._main, (LogicAndToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(AmpersandToken(self.tokPos),))

  def _caret(self, c, off, pos, cconsume, cpass):
    """A caret has been read"""
    if c and c == '=':
      return cconsume(self._main, (XorAssignToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(XorToken(self.tokPos),))

  def _pipe(self, c, off, pos, cconsume, cpass):
    """A pipe symbol has been read"""
    if c and c == '=':
      return cconsume(self._main, (OrAssignToken(self.tokPos),))
    elif c and c == '|':
      return cconsume(self._main, (LogicOrToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(OrToken(self.tokPos),))

  def _equal(self, c, off, pos, cconsume, cpass):
    """An equal sign has been read"""
    if c and c == '=':
      return cconsume(self._main, (EqualToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(AssignToken(self.tokPos),))

  def _excl(self, c, off, pos, cconsume, cpass):
    """An exclamation point has been read"""
    if c and c == '=':
      return cconsume(self._main, (NotEqualToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(LogicNotToken(self.tokPos),))

  def _colon(self, c, off, pos, cconsume, cpass):
    """A colon has been read"""
    if c and c == '>': # Right square bracket digraph
      self._closeSquare()
      return cconsume(self._main, (RSquareToken(self.tokPos),))
    else:
      return cpass(self._main, toks=(ColonToken(self.tokPos),))

def tokens(xs, raiseWarnings=False):
  """A generator that extracts just the tokens from a sequence returned by scan,
  optionally raising an exception if a warning is encountered."""
  for x in xs:
    assert isinstance(x, Token) or isinstance(x, ScanWarning)

    if isinstance(x, ScanWarning):
      if raiseWarnings:
        raise x
    else:
      yield x

def tokensAndWarnings(xs, warnings):
  """A generator that extracts just the tokens from a sequence returned by scan,
  populating a list of warnings with any warnings encountered."""
  for x in xs:
    assert isinstance(x, Token) or isinstance(x, ScanWarning)

    if isinstance(x, ScanWarning):
      warnings.append(x)
    else:
      yield x

def scan(str_, trace=False):
  """Scan an input string, returning a generator that yields tokens."""
  iter_ = ScannerIter(CScanner(), str_, trace)

  for tok in iter_:
    yield tok

  # The top level scanner should always consume all input
  assert iter_.done
