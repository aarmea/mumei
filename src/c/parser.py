"""
A parser for a subset of ANSI C

The current combinatorial implementation is inefficient, but is easy to
maintain.
"""

import itertools
import sys

from error import CompileError
import scanner
import syntree

def setMinimumRecursionLimit(minLimit):
  """Set the interpreter's recursion limit to be at least the given value."""
  if sys.getrecursionlimit() < minLimit:
    sys.setrecursionlimit(minLimit)

# This module relies heavily on recursion, so ensure that the stack is larger
# than the default.
setMinimumRecursionLimit(10000)

def partition(pred, iterable):
  """Return a pair of lists of elements that do and do not satisfy the
  predicate."""
  t1, t2 = itertools.tee(iterable)
  return list(filter(pred, t1)), list(itertools.ifilterfalse(pred, t2))

### Generic combinatorial parsers
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# These parsers are based on the combinatorial parsers from Haskell's
# Parsec library. Occasionally Haskell type signatures, like the one below,
# appear in comments to clarify the relationship between this code and a
# pure functional implementation.

# type Parser a = forall b. [Token]
#   -> (a -> [Token] -> ParseError -> b) -- consumed ok
#   -> (ParseError -> b)                 -- consumed err
#   -> (a -> [Token] -> ParseError -> b) -- empty ok
#   -> (ParseError -> b)                 -- empty err
#   -> b

# A Parser inspects the current state (list of tokens) and calls the
# continuation corresponding to the outcome of the parse. Parsers are
# additive monads, allowing them to be composed to produce more complicated
# parsers.

class ParseErrorMessage(tuple):
  """The base class of all parse error messages"""

  def __new__(cls, what):
    return tuple.__new__(cls, (what,))

  def __repr__(self):
    return "%s(what=%r)" % (type(self).__name__, self.what)

  what = property(lambda self: self[0])
  """A string identifying the expected or unexpected item"""

class Unexpected(ParseErrorMessage):
  """An unexpected error message"""

class Expecting(ParseErrorMessage):
  """An expecting error message"""

class ParseError(CompileError):
  """An error encountered while parsing a sequence of tokens"""

  def __init__(self, pos, msgs):
    CompileError.__init__(self, pos, "parse error")
    self.msgs = set(msgs)

  def __getMsg(self):
    """Return a single, combined error message for this error"""
    if self.msgs:
      exps, unexps = partition(lambda x: isinstance(x, Expecting), self.msgs)

      msgs = []
      if unexps:
        msgs.append("unexpected %s" % " or ".join(m.what for m in unexps))
      if exps:
        msgs.append("expecting %s" % " or ".join(m.what for m in exps))

      return "; ".join(msgs)
    else:
      return "unknown parse error"

  def isUnknown(self):
    """Return whether this error is unknown."""
    return bool(self.msgs)

  msg = property(__getMsg)
  """A single, combined error message for this error"""

def setExpect(e, what):
  """Set the expecting message of an error, removing existing expecting
  messages."""
  msgs = set(filter(lambda x: isinstance(x, Unexpected), e.msgs))
  msgs.add(Expecting(what))
  return ParseError(e.pos, msgs)

def unknownError(ts):
  """Return an unknown error at the current position."""
  if ts:
    return ParseError(ts[0].pos, [])
  else:
    # This only seems to occur on parses that get to the end of input and
    # never reaches the user. If an error occurrs then it is always overridden
    # by the new error message. If the parse succeeds then the error isn't
    # returned.
    return ParseError(None, [])

def unexpectError(ts, what):
  """Return an unexpected error at the current position."""
  return ParseError(ts[0].pos, [Unexpected(what)])

def mergeError(e1, e2):
  """Combine two errors, preserving errors from the longest parse."""
  if e1.pos is None:
    return e2
  elif e2.pos is None:
    return e1
  elif e1.pos.line > e2.pos.line:
    return e1
  elif e2.pos.line > e1.pos.line:
    return e2
  else:
    if e1.pos.col > e2.pos.col:
      return e1
    elif e2.pos.col > e1.pos.col:
      return e2
    else:
      return ParseError(e1.pos, e1.msgs.union(e2.msgs))

def runParser(p, ts):
  """Run a parser on a sequence of input tokens, returning the parsed value or
  raising a `ParseError` if the parse fails."""
  def ok(x, ts, e):
    return x

  def err(e):
    raise e

  return p(ts, ok, err, ok, err)

def mreturn(x):
  """Return a value in the parser monad."""
  # return :: a -> Parser a
  return lambda ts, _0, _1, eok, _2: eok(x, ts, unknownError(ts))

def mbind(p, f):
  """Sequentially compose two parsers."""
  # bind :: Parser a -> (a -> Parser b) -> Parser b
  def g(ts, cok, cerr, eok, eerr):
    def mcok(x, ts, e):
      neok = lambda x, ts, e_: cok(x, ts, mergeError(e, e_))
      neerr = lambda e_: cerr(mergeError(e, e_))
      return f(x)(ts, cok, cerr, neok, neerr)

    def meok(x, ts, e):
      neok = lambda x, ts, e_: eok(x, ts, mergeError(e, e_))
      neerr = lambda e_: cerr(mergeError(e, e_))
      return f(x)(ts, cok, cerr, neok, neerr)

    return p(ts, mcok, cerr, meok, eerr)

  return g

def mzero():
  """A parser that always fails without consuming any input (monadic zero)"""
  return lambda ts, _0, _1, _2, eerr: eerr(unknownError(ts))

def mplus(p, q):
  """A parser that combines two parsers, succeeding if either parser succeeds
  (monadic plus)"""
  def f(ts, cok, cerr, eok, eerr):
    def meerr(e):
      neok = lambda x, ts, e_: eok(x, ts, mergeError(e, e_))
      neerr = lambda e_: eerr(mergeError(e, e_))
      return q(ts, cok, cerr, neok, neerr)

    return p(ts, cok, cerr, eok, meerr)

  return f

def token(pred):
  """Parse a token that satisfies the predicate."""
  def f(ts, cok, cerr, eok, eerr):
    t, ts_ = ts[0], ts[1:]
    if pred(t):
      return cok(t, ts_, unknownError(ts_))
    else:
      return eerr(unexpectError(ts, str(t)))

  return f

def label(p, what):
  """Change the expecting message for a parser."""
  def f(ts, cok, cerr, eok, eerr):
    meok = lambda x, ts, e: eok(x, ts,
      e if e.isUnknown() else setExpect(e, what))
    meerr = lambda e: eerr(setExpect(e, what))
    return p(ts, cok, cerr, meok, meerr)

  return f

def try_(p):
  """Parse with `p`, but without consuming any input if an error occurs."""
  return lambda ts, cok, _, eok, eerr: p(ts, cok, eerr, eok, eerr)

def lookAhead(p):
  """Parse `p` without consuming any input. This function consumes input if `p`
  fails and consumes input."""
  def f(ts, cok, cerr, eok, eerr):
    mcok = lambda x, _, e: eok(x, ts, e)
    return p(ts, mcok, cerr, eok, eerr)

  return f

def manyErr(*_):
  """A parser that accepts an empty sequence was passed to many."""
  assert False

def many(p):
  """Accept zero or more occurrences of sequences accepted by `p`."""
  def f(ts, cok, cerr, eok, eerr):
    def walk(xs):
      def g(x, ts, e):
        meerr = lambda e: cok(xs + [x], ts, e)
        return p(ts, walk(xs + [x]), cerr, manyErr, meerr)

      return g

    return p(ts, walk([]), cerr, manyErr, lambda e: eok([], ts, e))

  return f

def many1(p):
  """Accept one or more occurrences of sequences accepted by `p`."""
  return mbind(p, lambda x: mbind(many(p), lambda xs: mreturn([x] + xs)))

def option(x, p):
  """Apply `p`, returning `x` if `p` fails without consuming input."""
  return mplus(p, mreturn(x))

### Grammar-specific combinatorial parsers
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

# The parsers in the section are based on the ANSI C syntax specification.
# The parsers for each non-terminal are preceeded by the part of the C
# grammar that they correspond to.

# Token parsers
identifierToken = token(lambda t: isinstance(t, scanner.IdentifierToken))
keywordToken = lambda kw: token(
  lambda t: isinstance(t, scanner.KeywordToken) and t.val == kw)
intToken = token(lambda t: isinstance(t, scanner.IntToken))
longToken = token(lambda t: isinstance(t, scanner.LongToken))
uintToken = token(lambda t: isinstance(t, scanner.UIntToken))
ulongToken = token(lambda t: isinstance(t, scanner.ULongToken))
charToken = token(lambda t: isinstance(t, scanner.CharToken))
wcharToken = token(lambda t: isinstance(t, scanner.WCharToken))
floatToken = token(lambda t: isinstance(t, scanner.FloatToken))
doubleToken = token(lambda t: isinstance(t, scanner.DoubleToken))
longDoubleToken = token(lambda t: isinstance(t, scanner.LongDoubleToken))
semicolonToken = token(lambda t: isinstance(t, scanner.SemicolonToken))
lcurlyToken = token(lambda t: isinstance(t, scanner.LCurlyToken))
rcurlyToken = token(lambda t: isinstance(t, scanner.RCurlyToken))
commaToken = token(lambda t: isinstance(t, scanner.CommaToken))
assignToken = token(lambda t: isinstance(t, scanner.AssignToken))
lparenToken = token(lambda t: isinstance(t, scanner.LParenToken))
rparenToken = token(lambda t: isinstance(t, scanner.RParenToken))
addToken = token(lambda t: isinstance(t, scanner.AddToken))
starToken = token(lambda t: isinstance(t, scanner.StarToken))
lessThanToken = token(lambda t: isinstance(t, scanner.LessThanToken))
eofToken = token(lambda t: isinstance(t, scanner.EOFToken))

# primary-expression:
#   identifier
#   constant
#   string-literal # XXX Not implemented
#   '(' expression ')'
varExpr = (
  mbind(identifierToken, lambda id_:
  mreturn(syntree.VarExpr(id_.val))))
intExpr = (
  mbind(intToken, lambda const:
  mreturn(syntree.ConstExpr(syntree.IntType(), const.val))))
longExpr = (
  mbind(longToken, lambda const:
  mreturn(syntree.ConstExpr(syntree.LongType(), const.val))))
uintExpr = (
  mbind(uintToken, lambda const:
  mreturn(syntree.ConstExpr(syntree.UIntType(), const.val))))
ulongExpr = (
  mbind(ulongToken, lambda const:
  mreturn(syntree.ConstExpr(syntree.ULongType(), const.val))))
floatExpr = (
  mbind(floatToken, lambda const:
  mreturn(syntree.ConstExpr(syntree.FloatType(), const.val))))
doubleExpr = (
  mbind(doubleToken, lambda const:
  mreturn(syntree.ConstExpr(syntree.DoubleType(), const.val))))
longDoubleExpr = (
  mbind(longDoubleToken, lambda const:
  mreturn(syntree.ConstExpr(syntree.LongDoubleType(), const.val))))
charExpr = (
  mbind(charToken, lambda const:
  mreturn(syntree.ConstExpr(syntree.CharType(), const.val))))
wcharExpr = (
  mbind(wcharToken, lambda const:
  mreturn(syntree.ConstExpr(syntree.WCharType(), const.val))))
constExpr = mplus(mplus(mplus(mplus(mplus(mplus(mplus(mplus(intExpr,
  longExpr), uintExpr), ulongExpr), floatExpr), doubleExpr), longDoubleExpr),
  charExpr), wcharExpr)
nestedExpr = (
  mbind(lparenToken, lambda _:
  mbind(expr, lambda expr_:
  mbind(rparenToken, lambda _:
  mreturn(expr_)))))
primaryExpr = mplus(mplus(varExpr, constExpr), nestedExpr)

# argument-expression-list-suffix:
#   ',' assignment-expression argument-expression-list-suffix?
argExprListSuffix = (
  mbind(commaToken, lambda _:
  mbind(assignExpr, lambda expr_:
  mbind(option([], argExprListSuffix), lambda exprs:
  mreturn([expr_] + exprs)))))

# argument-expression-list:
#   assignment-expression argument-expression-list-suffix?
argExprList = (
  mbind(lambda *a: assignExpr(*a), lambda expr_: # defer
  mbind(option([], argExprListSuffix), lambda exprs:
  mreturn([expr_] + exprs))))

# postfix-expression-suffix:
#   '[' expression ']' postfix-expression-suffix? # XXX Not implemented
#   '(' argument-expression-list? ')' postfix-expression-suffix?
#   ',' identifier postfix-expression-suffix? # XXX Not implemented
#   '->' identifier postfix-expression-suffix? # XXX Not implemented
#   '++' postfix-expression-suffix? # XXX Not implemented
#   '--' postfix-expression-suffix? # XXX Not implemented
funPostExprSuffix = (
  mbind(lparenToken, lambda _:
  mbind(option([], argExprList), lambda argExprs:
  mbind(rparenToken, lambda _:
  mbind(option([], funPostExprSuffix), lambda argExprss:
  mreturn([argExprs] + argExprss))))))

postfixExprSuffix = funPostExprSuffix

# postfix-expression:
#   primary-expression postfix-expression-suffix?
postfixExpr = (
  mbind(primaryExpr, lambda expr_:
  mbind(option([], funPostExprSuffix), lambda argExprss:
  mreturn(reduce(lambda funExpr, argExprs:
    syntree.CallExpr(funExpr, argExprs), argExprss, expr_)))))

# unary-expression:
#   postfix-expression
#   '++' unary-expression # XXX Not implemented
#   '--' unary-expression # XXX Not implemented
#   unary-operator cast-expression # XXX Only implemented for '*'
#   'sizeof' unary-expression # XXX Not implemented
#   'sizeof' '(' type-name ')' # XXX Not implemented
#
# unary-operator:
#   '&' # XXX Not implemented
#   '*'
#   '+' # XXX Not implemented
#   '-' # XXX Not implemented
#   '~' # XXX Not implemented
#   '!' # XXX Not implemented
derefExpr = (
  mbind(starToken, lambda _:
  mbind(castExpr, lambda expr_:
  mreturn(syntree.DerefExpr(expr_)))))
unaryExpr = mplus(postfixExpr, derefExpr)

# cast-expression:
#   unary-expression
#   '(' type-name ')' cast-expression
castExpr = unaryExpr

# multiplicative-expression:
#   cast-expression multiplicative-expression-suffix?
#
# multiplicative-expression-suffix:
#   '*' cast-expression multiplicative-expression-suffix? # XXX Not implemented
#   '/' cast-expression multiplicative-expression-suffix? # XXX Not implemented
#   '%' cast-expression multiplicative-expression-suffix? # XXX Not implemented
mulExpr = castExpr

# additive-expression-suffix:
#   '+' multiplicative-expression additive-expression-suffix?
#   '-' multiplicative-expression additive-expression-suffix? # XXX Not implemented
addExprSuffix = (
  mbind(addToken, lambda _:
  mbind(mulExpr, lambda expr_:
  mbind(option([], addExprSuffix), lambda exprs:
  mreturn([expr_] + exprs)))))

# additive-expression:
#   multiplicative-expression additive-expression-suffix?
addExpr = (
  mbind(mulExpr, lambda expr_:
  mbind(option([], addExprSuffix), lambda exprs:
  mreturn(reduce(lambda lexpr, rexpr:
    syntree.AddExpr(lexpr, rexpr), exprs, expr_)))))

# shift-expression:
#   additive-expression shift-expression-suffix?
#
# shift-expression-suffix:
#   '<<' additive-expression shift-expression-suffix? # XXX Not implemented
#   '>>' additive-expression shift-expression-suffix? # XXX Not implemented
shiftExpr = addExpr

# relational-expression-suffix:
#   '<' shift-expression relational-expression-suffix?
#   '>' shift-expression relational-expression-suffix? # XXX Not implemented
#   '<=' shift-expression relational-expression-suffix? # XXX Not implemented
#   '>=' shift-expression relational-expression-suffix? # XXX Not implemented
relExprSuffix = (
  mbind(lessThanToken, lambda _:
  mbind(shiftExpr, lambda expr_:
  mbind(option([], relExprSuffix), lambda exprs:
  mreturn([expr_] + exprs)))))

# relational-expression:
#   shift-expression relational-expression-suffix?
relExpr = (
  mbind(shiftExpr, lambda expr_:
  mbind(option([], relExprSuffix), lambda exprs:
  mreturn(reduce(lambda lexpr, rexpr:
    syntree.LessThanExpr(lexpr, rexpr), exprs, expr_))))) # XXX Only handles '<'

# equality-expression:
#   relational-expression equality-expression-suffix?
#
# equality-expression-suffix:
#   '==' relational-expression equality-expression-suffix? # XXX Not implemented
#   '!=' relational-expression equality-expression-suffix? # XXX Not implemented
eqExpr = relExpr

# and-expression:
#   equality-expression and-expression-suffix?
#
# and-expression-suffix:
#   '&' equality-expression and-expression-suffix? # XXX Not implemented
andExpr = eqExpr

# exclusive-or-expression:
#   and-expression exclusive-or-expression-suffix?
#
# exclusive-or-expression-suffix:
#   '^' and-expression exclusive-or-expression-suffix? # XXX Not implemented
exclOrExpr = andExpr

# inclusive-or-expression:
#   exclusive-or-expression inclusive-of-expression-suffix?
#
# inclusive-or-expression-suffix:
#   '|' exclusive-or-expression inclusive-of-expression-suffix? # XXX Not impl.
inclOrExpr = exclOrExpr

# logical-and-expression:
#   inclusive-or-expression logical-and-expression-suffix? # XXX Not implemented
#
# logical-and-expression-suffix:
#   '&&' inclusive-or-expression logical-and-expression-suffix?
logicAndExpr = inclOrExpr

# logical-or-expression:
#   logical-and-expression logical-or-expression-suffix?
#
# logical-or-expression-suffix:
#   '||' logical-and-expression logical-or-expression-suffix? # XXX Not impl.
logicOrExpr = logicAndExpr

# conditional-expression:
#   logical-or-expression
#   logical-or-expression '?' expression ':' conditional-expression # XXX
condExpr = logicOrExpr

# assignment-expression:
#   conditional-expression
#   unary-expression assignment-operator assignment-expression # XXX Only '='
assignExprLook = lookAhead(mbind(unaryExpr, lambda _: assignToken))
assignExpr_ = (
  mbind(try_(assignExprLook), lambda _:
  mbind(unaryExpr, lambda lexpr:
  mbind(assignToken, lambda _:
  mbind(assignExpr, lambda rexpr:
  mreturn(syntree.AssignExpr(lexpr, None, rexpr)))))))
assignExpr = mplus(assignExpr_, condExpr)

# expression:
#   assignment-expression expression-suffix?
#
# expression-suffix:
#   ',' assignment-expression expression-suffix? # XXX Not implemented
expr = assignExpr

# jump-statement:
#   'goto' identifier ';' # XXX Not implemented
#   'continue' ';' # XXX Not implemented
#   'break' ';' # XXX Not implemented
#   'return' expression? ';'
returnStmt = (
  mbind(keywordToken("return"), lambda _:
  mbind(option(None, expr), lambda expr_:
  mbind(semicolonToken, lambda _:
  mreturn(syntree.ReturnStmt(expr_))))))
jumpStmt = returnStmt

# iteration-statement:
#   'while' '(' expression ')' statement
#   'do' statement 'while' '(' expression ')' ';' # XXX Not implemented
#   'for' '(' expression? ';' expression? ';' expression ')' statement # XXX
#   'for' '(' declaration expression? ';' expression? ')' statement # XXX
iterationStmt = (
  mbind(keywordToken("while"), lambda _:
  mbind(lparenToken, lambda _:
  mbind(expr, lambda expr_:
  mbind(rparenToken, lambda _:
  mbind(stmt, lambda stmt:
  mreturn(syntree.WhileStmt(expr_, stmt))))))))

# selection-statement:
#   'if' '(' expression ')' statement
#   'if' '(' expression ')' statement 'else' statement
#   'switch' '(' expression ')' statement # XXX Not implemented
selectionStmt = (
  mbind(keywordToken("if"), lambda _:
  mbind(lparenToken, lambda _:
  mbind(expr, lambda expr_:
  mbind(rparenToken, lambda _:
  mbind(stmt, lambda tstmt:
  mbind(option(None, mbind(keywordToken("else"), lambda _: stmt)), lambda fstmt:
  mreturn(syntree.IfStmt(expr_, tstmt, fstmt)))))))))

# expression-statement:
#  expression? ';'
exprStmtLook = lookAhead(mbind(option(None, expr), lambda _: semicolonToken))
exprStmt = (
  mbind(try_(exprStmtLook), lambda _:
  mbind(option(None, expr), lambda expr_:
  mbind(semicolonToken, lambda _:
  mreturn(syntree.ExprStmt(expr_))))))

# compound-statement:
#   '{' declaration-list? statement-list? '}'
compoundStmt = (
  mbind(lcurlyToken, lambda _:
  mbind(declList0, lambda decls:
  mbind(stmtList0, lambda stmts:
  mbind(rcurlyToken, lambda _:
  mreturn(syntree.CompoundStmt(decls, stmts)))))))

# statement:
#   labeled-statement # XXX Not implemented
#   compound-statement
#   expression-statement
#   selection-statement
#   iteration-statement
#   jump-statement
stmt = mplus(mplus(mplus(mplus(compoundStmt, exprStmt), selectionStmt),
  iterationStmt), jumpStmt)

# statement-list:
#   statement+
stmtList = many1(stmt)
stmtList0 = many(stmt)

# identifier-list:
#   identifier identifier-list-suffix?
#
# identifier-list-suffix:
#   ',' identifier identifier-list-suffix?
identifierList = mzero() # XXX Not implemented

# parameter-declaration:
#   declaration-specifiers declarator
#   declaration-specifiers abstract-declarator? # XXX Not implemented (f(void))
def mkParamDecl(specs, declarator_):
  storageClassSpec, typeSpec, signSpec, sizeSpec = normalizeDeclSpecs(specs)
  declarator_.applySpecs(storageClassSpec, typeSpec)
  return syntree.ParamDecl(declarator_)

paramDecl = (
  mbind(lambda *a: declSpecs(*a), lambda specs: # defer
  mbind(declarator, lambda declarator_:
  mreturn(mkParamDecl(specs, declarator_)))))

# parameter-list-suffix:
#   ',' parameter-declaration parameter-list-suffix?
paramListSuffix = (
  mbind(commaToken, lambda _:
  mbind(paramDecl, lambda param:
  mbind(option([], paramListSuffix), lambda params:
  mreturn([param] + params)))))

# parameter-list:
#   parameter-declaration parameter-list-suffix?
paramList = (
  mbind(paramDecl, lambda param:
  mbind(option([], paramListSuffix), lambda params:
  mreturn([param] + params))))

# parameter-type-list:
#   parameter-list
#   parameter-list ',' '...' # XXX Not implemented
paramTypeList = paramList

# pointer:
#   '*' type-qualifier-list?
#   '*' type-qualifier-list? pointer
def normalizeTypeQuals(quals):
  isConst = False
  isVolatile = False

  for qual in quals:
    if isinstance(qual, syntree.ConstTypeQual):
      if isConst:
        pass # XXX Warning: duplicate 'const'
      isConst = True
    elif isinstance(qual, syntree.VolatileTypeQual):
      if isVolatile:
        pass # XXX Warning: duplicate 'volatile'
      isVolatile = True

  return (isConst, isVolatile)

pointer = (
  mbind(starToken, lambda _:
  mbind(typeQualList0, lambda typeQuals:
  mbind(option([], pointer), lambda cvs:
  mreturn([normalizeTypeQuals(typeQuals)] + cvs)))))

# direct-declarator-suffix:
#   '[' constant-expression? ']' direct-declarator-suffix? # XXX Not implemented
#   '(' parameter-type-list ')' direct-declarator-suffix?
#   '(' identifier-list? ')' direct-declarator-suffix?
paramDirectDeclaratorSuffixLook = lookAhead(
  mbind(lparenToken, lambda _:
    paramTypeList))
paramDirectDeclaratorSuffix = (
  mbind(try_(paramDirectDeclaratorSuffixLook), lambda _:
  mbind(lparenToken, lambda _:
  mbind(paramTypeList, lambda params:
  mbind(rparenToken, lambda _:
  mreturn(syntree.ParamDeclaratorSuffix(params)))))))
krDirectDeclaratorSuffix = (
  mbind(lparenToken, lambda _:
  mbind(option([], identifierList), lambda ids:
  mbind(rparenToken, lambda _:
  mreturn(syntree.KRDeclaratorSuffix(ids))))))
directDeclaratorSuffix = mplus(paramDirectDeclaratorSuffix,
  krDirectDeclaratorSuffix)

# direct-declarator:
#   identifier direct-declarator-suffix?
#   '(' declarator ')' direct-declarator-suffix?
nameDirectDeclarator = (
  mbind(identifierToken, lambda id_:
  mreturn(syntree.NameDeclarator(id_.val))))
nestedDirectDeclarator = (
  mbind(lparenToken, lambda _:
  mbind(declarator, lambda declarator:
  mbind(rparenToken, lambda _:
  mreturn(declarator)))))
directDeclarator = (
  mbind(mplus(nameDirectDeclarator, nestedDirectDeclarator), lambda direct:
  mbind(many(directDeclaratorSuffix), lambda suffixes:
  mreturn(syntree.DirectDeclarator.fromSuffixes(direct, suffixes)))))

# declarator:
#   pointer? direct-declarator
def mkPointerDeclarator(cvs, direct):
  return reduce(
    lambda declarator, cv: syntree.PointerDeclarator(cv, declarator),
    cvs, direct)

pointerDeclarator = (
  mbind(try_(lookAhead(starToken)), lambda _:
  mbind(pointer, lambda cvs:
  mbind(directDeclarator, lambda direct:
  mreturn(mkPointerDeclarator(cvs, direct))))))
declarator = mplus(pointerDeclarator, directDeclarator)

# type-qualifier:
#   'const'
#   'volatile'
constTypeQual = (
  mbind(keywordToken("const"), lambda t:
  mreturn(syntree.ConstTypeQual(t.pos))))
volatileTypeQual = (
  mbind(keywordToken("volatile"), lambda t:
  mreturn(syntree.VolatileTypeQual(t.pos))))
typeQual = mplus(constTypeQual, volatileTypeQual)

# type-qualifier-list:
#   type-qualifier+
typeQualList = many1(typeQual)
typeQualList0 = many(typeQual)

# type-specifier:
#   'void'
#   'char'
#   'short'
#   'int'
#   'long'
#   'float'
#   'double'
#   'signed'
#   'unsigned'
#   struct-or-union-specifier # XXX Not implemented
#   enum-specifier # XXX Not implemented
#   typedef-name # XXX Not implemented
voidTypeSpec = (
  mbind(keywordToken("void"), lambda t:
  mreturn(syntree.VoidTypeSpec(t.pos))))
charTypeSpec = (
  mbind(keywordToken("char"), lambda t:
  mreturn(syntree.CharTypeSpec(t.pos))))
shortTypeSpec = (
  mbind(keywordToken("short"), lambda t:
  mreturn(syntree.ShortTypeSpec(t.pos))))
intTypeSpec = (
  mbind(keywordToken("int"), lambda t:
  mreturn(syntree.IntTypeSpec(t.pos))))
longTypeSpec = (
  mbind(keywordToken("long"), lambda t:
  mreturn(syntree.LongTypeSpec(t.pos))))
floatTypeSpec = (
  mbind(keywordToken("float"), lambda t:
  mreturn(syntree.FloatTypeSpec(t.pos))))
doubleTypeSpec = (
  mbind(keywordToken("double"), lambda t:
  mreturn(syntree.DoubleTypeSpec(t.pos))))
signedTypeSpec = (
  mbind(keywordToken("signed"), lambda t:
  mreturn(syntree.SignedTypeSpec(t.pos))))
unsignedTypeSpec = (
  mbind(keywordToken("unsigned"), lambda t:
  mreturn(syntree.UnsignedTypeSpec(t.pos))))
typeSpec = mplus(mplus(mplus(mplus(mplus(mplus(mplus(mplus(voidTypeSpec,
  charTypeSpec), shortTypeSpec), intTypeSpec), longTypeSpec), floatTypeSpec),
  doubleTypeSpec), signedTypeSpec), unsignedTypeSpec)

# storage-class-specifier
#   'typedef'
#   'extern'
#   'static'
#   'auto'
#   'register'
typedefStorageClassSpec = (
  mbind(keywordToken("typedef"), lambda t:
  mreturn(syntree.TypedefStorageClassSpec(t.pos))))
externStorageClassSpec = (
  mbind(keywordToken("extern"), lambda t:
  mreturn(syntree.ExternStorageClassSpec(t.pos))))
staticStorageClassSpec = (
  mbind(keywordToken("static"), lambda t:
  mreturn(syntree.StaticStorageClassSpec(t.pos))))
autoStorageClassSpec = (
  mbind(keywordToken("auto"), lambda t:
  mreturn(syntree.AutoStorageClassSpec(t.pos))))
registerStorageClassSpec = (
  mbind(keywordToken("register"), lambda t:
  mreturn(syntree.RegisterStorageClassSpec(t.pos))))
storageClassSpec = mplus(mplus(mplus(mplus(typedefStorageClassSpec,
  externStorageClassSpec), staticStorageClassSpec), autoStorageClassSpec),
  registerStorageClassSpec)

# init-declarator:
#   declarator
#   declarator '=' initializer # XXX Not implemented
initDeclarator = declarator

# init-declarator-list-suffix:
#   ',' init-declarator init-declarator-list-suffix?
initDeclaratorListSuffix = (
  mbind(commaToken, lambda _:
  mbind(initDeclarator, lambda init:
  mbind(option([], initDeclaratorListSuffix), lambda inits:
  mreturn([init] + inits)))))

# init-declarator-list:
#   init-declarator init-declarator-list-suffix?
initDeclaratorList = (
  mbind(initDeclarator, lambda init:
  mbind(option([], initDeclaratorListSuffix), lambda inits:
  mreturn([init] + inits))))

# declaration-specifiers:
#   storage-class-specifier declaration-specifiers?
#   type-specifier declaration-specifiers?
#   type-qualifier declaration-specifiers?
declSpec = mplus(mplus(storageClassSpec, typeSpec), typeQual)
declSpecs = many1(declSpec)
declSpecs0 = many(declSpec)

def normalizeDeclSpecs(specs):
  # At most one storage-class specifier may be given in the declaration
  # specifiers in a declaration ($3.5.1).
  storageClassSpec = None
  typeSpec = None
  signSpec = None
  sizeSpec = None

  for spec in specs:
    if isinstance(spec, syntree.StorageClassSpec):
      if storageClassSpec is None:
        storageClassSpec = spec
      else:
        if type(storageClassSpec) is type(spec):
          raise CompileError(spec.pos, "duplicate %s" % spec) # XXX no str(spec)
        else:
          raise CompileError(spec.pos, "multiple storage classes in"
            " declaration specifiers")

    elif isinstance(spec, syntree.TypeSpec):
      if typeSpec is None:
        typeSpec = spec
      else:
        raise CompileError(spec.pos, "two or more data types in declaration"
          " specifiers")

    # XXX signSpec, sizeSpec not implemented

  return (storageClassSpec, typeSpec, signSpec, sizeSpec)

# declaration:
#   declaration-specifiers init-declarator-list? ';'
def mkDecl(specs, inits):
  storageClassSpec, typeSpec, signSpec, sizeSpec = normalizeDeclSpecs(specs)

  # XXX signSpec, sizeSpec unused

  for init in inits:
    init.applySpecs(storageClassSpec, typeSpec)

  return syntree.Decl(inits)

decl = (
  mbind(declSpecs, lambda specs:
  mbind(option([], initDeclaratorList), lambda inits:
  mbind(semicolonToken, lambda _:
  mreturn(mkDecl(specs, inits))))))

# declaration-list:
#   declaration+
declList = many1(decl)
declList0 = many(decl)

# function-definition:
#   declaration-specifiers? declarator declaration-list? compound-statement
def mkFunDef(specs, declarator_, decls, stmt):
  storageClassSpec, typeSpec, signSpec, sizeSpec = normalizeDeclSpecs(specs)

  # The storage class specifier can only be extern or static for functions, and
  # is extern by default.
  if storageClassSpec is None:
    storageClassSpec = syntree.ExternStorageClassSpec(None)
  elif type(storageClassSpec) not in (syntree.ExternStorageClassSpec,
    syntree.StaticStorageClassSpec):
    raise CompileError(storageClassSpec.pos, "function definition declared '%s'"
      % storageClassSpec) # XXX no str(storageClassSpec)

  # XXX typeSpec can't be array

  # XXX signSpec, sizeSpec unused

  declarator_.applySpecs(storageClassSpec, typeSpec)

  return syntree.FunDef(declarator_, decls, stmt)

# We can't tell whether this is a function definition or a declaration until we
# get to the compound statement, if any.
funDefLook = lookAhead(
  mbind(declSpecs0, lambda _:
  mbind(declarator, lambda _:
  mbind(declList0, lambda _:
    lcurlyToken))))
funDef_ = (
  mbind(try_(funDefLook), lambda _:
  mbind(declSpecs0, lambda specs:
  mbind(declarator, lambda declarator_:
  mbind(declList0, lambda decls:
  mbind(compoundStmt, lambda stmt:
  mreturn(mkFunDef(specs, declarator_, decls, stmt))))))))
funDef = label(funDef_, "function definition")

# external-declaration:
#   function-definition
#   declaration
externalDecl = mplus(funDef, decl)

# translation-unit:
#   external-declaration+
translationUnit = (
  mbind(many1(externalDecl), lambda decls:
  mreturn(syntree.TranslationUnit(decls))))

def parse(ts):
  """Parse a C program, returning a syntax tree."""
  parser = (
    mbind(translationUnit, lambda tu:
    mbind(eofToken, lambda _: mreturn(tu))))
  return runParser(parser, ts)
