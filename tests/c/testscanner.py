"""
Test cases for c.scanner
"""

import unittest

import tests.arbitrary as arbitrary
from tests.arbitrary import forall

from c.scanner import *

# Type size limits

INT_BITS = 16

MIN_INT = 0 # C uses unary '-' for negative numbers
MAX_INT = 1 << (INT_BITS - 1) # 2**(MAX_BITS - 1) for negative ints

# The main test class

class TestScanner(unittest.TestCase):
  """A test class for the c.scanner module"""

  def test_scanKeywords(self):
    """scan yields keyword tokens for keyword strings"""
    for s in ["auto", "break", "case", "char", "const", "continue", "default",
      "do", "double", "else", "enum", "extern", "float", "for", "goto", "if",
      "int", "long", "register", "return", "short", "signed", "sizeof",
      "static", "struct", "switch", "typedef", "union", "unsigned", "void",
      "volatile", "while"]:
      gen = scan(s)
      tok = next(gen)
      self.assertEqual(type(tok), KeywordToken)
      self.assertEqual(tok.val, s)

  @forall(val=arbitrary.ints(lower=MIN_INT, upper=MAX_INT),
    base=arbitrary.items([8, 10, 16]))
  def test_scanInts(self, val, base):
    """scan yields int tokens for valid int strings"""
    fmt = {8: "0%o", 10: "%d", 16: "0x%x"}[base]
    s = fmt % val
    gen = scan(s)
    tok = next(gen)
    self.assertEqual(type(tok), IntToken)
    self.assertEqual(tok.val, val)

  def test_scanOperators(self):
    """scan yields the expected token types for operator strings"""
    # These operators are from $3.1.5 in the ANSI C standard
    for s, type_ in [ (".", PeriodToken)
                    , ("->", ArrowToken)
                    , ("++", IncrementToken)
                    , ("--", DecrementToken)
                    , ("&", AmpersandToken)
                    , ("*", StarToken)
                    , ("+", AddToken)
                    , ("-", SubToken)
                    , ("~", NotToken)
                    , ("!", LogicNotToken)
                    , ("/", DivToken)
                    , ("%", ModToken)
                    , ("<<", LeftShiftToken)
                    , (">>", RightShiftToken)
                    , ("<", LessThanToken)
                    , (">", GreaterThanToken)
                    , ("<=", LessThanEqualToken)
                    , (">=", GreaterThanEqualToken)
                    , ("==", EqualToken)
                    , ("!=", NotEqualToken)
                    , ("^", XorToken)
                    , ("|", OrToken)
                    , ("&&", LogicAndToken)
                    , ("||", LogicOrToken)
                    , ("=", AssignToken)
                    , ("*=", MulAssignToken)
                    , ("/=", DivAssignToken)
                    , ("%=", ModAssignToken)
                    , ("+=", AddAssignToken)
                    , ("-=", SubAssignToken)
                    , ("<<=", LeftShiftAssignToken)
                    , (">>=", RightShiftAssignToken)
                    , ("&=", AndAssignToken)
                    , ("^=", XorAssignToken)
                    , ("|=", OrAssignToken)
                    , (",", CommaToken)
                    ]:
      gen = scan(s)
      tok = next(gen)
      self.assertEqual(type(tok), type_)
