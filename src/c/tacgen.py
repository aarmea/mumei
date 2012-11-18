"""
A three-address code generator for a subset of ANSI C
"""

import itertools

from error import CompileError
import syntree
from threeaddr.threeaddr import *

UNINITIALIZED_WORD = 0xCCCC
"""A value stored in uninitialized space"""

class Env(dict):
  """An environment contains all variable names and their associated variable
  objects that are accessible from the current scope."""

  def __init__(self, outer=None):
    self.outer = outer

  def find(self, var):
    """Find the environment in the stack that contains the given variable name,
    or None if the variable is not found in any environment."""
    return self if var in self else (self.outer.find(var) if self.outer is not
      None else None)

class TACGenerator(object):
  """A three-address code generator that generates code from a C syntax tree

  visitXXX functions accept a syntax tree node and return a node-specific value.

  visitXXX functions for expressions accept a syntax tree node and a boolean
  parameter that determines whether to return an lvalue or an rvalue variable.
  In the case of an lvalue, a variable containing the address of the result is
  returned.
  """

  def __init__(self):
    # Temporary variable and label generators
    self.varGen = AutoGen("@t", LocalVar)
    self.labelGen = AutoGen("@l", GlobalVar)

    # Code storage
    self.code = []

    # The current environment
    self.env = Env()

  def __genLValue(self, expr, label):
    """Generate code to get an address from an expression, raising an error if
    the expression is not an lvalue."""
    addrVar = expr.accept(self, True)

    if addrVar is None:
      raise CompileError(expr.pos, "lvalue required as %s" % label)

    return addrVar

  def _pushEnv(self):
    """Push an empty environment onto the environment stack"""
    self.env = Env(self.env)

  def _popEnv(self):
    """Remove the current environment from the environment stack"""
    self.env = self.env.outer

  def visitConstExpr(self, node, lvalue=False):
    """Generate code for a constant expression"""
    # A constant is not an lvalue
    if lvalue:
      return None

    # Allocate a temporary variable for the constant
    var = next(self.varGen)
    # Assign the constant value to the variable
    self.code.append(Assign(var, node.val))

    return var

  def visitVarExpr(self, node, lvalue=False):
    """Generate code for a variable expression"""
    # Look up the variable binding
    varEnv = self.env.find(node.id)

    # Check for undefined variables
    # XXX This should be done before code generation
    if varEnv is None:
      raise CompileError(node.pos, "`%s' undeclared" % node.id)

    var = varEnv[node.id]

    if lvalue:
      # Generate a variable containing the address of the result
      addrVar = next(self.varGen)
      self.code.append(AddressOf(addrVar, var))

      return addrVar
    else:
      return var

  def visitIncExpr(self, node, lvalue, post):
    """Generate code for an increment expression"""
    # The result of an increment expression is not an lvalue
    if lvalue:
      return None

    # Allocate a temporary variable for the result
    rvar = next(self.varGen)
    # Generate code for the value of the variable
    var = node.expr.accept(self)
    # Generate code for the address of the variable
    addrVar = self.__genLValue(node.expr, "increment operand")
    # Generate the increment instruction
    self.code.append(Add(rvar, var, 1))
    # Store the result in the lvalue
    self.code.append(Store(addrVar, rvar))

    if post:
      return var
    else:
      return rvar

  def visitDecExpr(self, node, lvalue, post):
    """Generate code for a decrement expression"""
    # The result of a decrement expression is not an lvalue
    if lvalue:
      return None

    # Allocate a temporary variable for the result
    rvar = next(self.varGen)
    # Generate code for the value of the variable
    var = node.expr.accept(self)
    # Generate code for the address of the variable
    addrVar = self.__genLValue(node.expr, "decrement operand")
    # Generate the decrement instruction
    self.code.append(Sub(rvar, var, 1))
    # Store the result in the lvalue
    self.code.append(Store(addrVar, rvar))

    if post:
      return var
    else:
      return rvar

  def visitPostIncExpr(self, node, lvalue=False):
    """Generate code for a post-increment expression"""
    return self.visitIncExpr(node, lvalue, True)

  def visitPostDecExpr(self, node, lvalue=False):
    """Generate code for a post-decrement expression"""
    return self.visitDecExpr(node, lvalue, True)

  def visitCallExpr(self, node, lvalue=False):
    """Generate code for a function call expression"""
    # The result of a call is not an lvalue
    if lvalue:
      return None

    # Allocate a temporary variable for the return value
    var = next(self.varGen)
    # Generate code to grab the function address
    funAddrVar = node.expr.accept(self, True)

    # Check for invalid functions
    # XXX This should be done in the type checker
    if funAddrVar is None:
      raise CompileError(node.expr.pos, "called object is not a function")

    # Generate code for the expressions used as function arguments, pushing the
    # actual arguments on the parameter stack.
    for expr in node.argExprs:
      argVar = expr.accept(self)
      self.code.append(PushParam(argVar))

    # Generate the call instruction
    self.code.append(Call(var, funAddrVar))
    # Clean up the stack
    self.code.append(PopParams(len(node.argExprs)))

    return var

  def visitPreIncExpr(self, node, lvalue=False):
    """Generate code for a pre-increment expression"""
    return self.visitIncExpr(node, lvalue, False)

  def visitPreDecExpr(self, node, lvalue=False):
    """Generate code for a pre-decrement expression"""
    return self.visitDecExpr(node, lvalue, False)

  def visitAddrOfExpr(self, node, lvalue=False):
    """Generate code for an address-of expression"""
    # The result of an address-of expression is not an lvalue
    if lvalue:
      return None

    # Generate code for the address of the expression result
    return self.__genLValue(node.expr, "unary `&' operand")

  def visitDerefExpr(self, node, lvalue=False):
    """Generate code for a dereference expression"""
    # Generate code for the expression to dereference
    addrVar = node.expr.accept(self)

    if lvalue:
      return addrVar
    else:
      # Allocate a temporary variable for the value at the memory location.
      var = next(self.varGen)
      # Load the value at the memory location into the temporary variable.
      self.code.append(Load(var, addrVar))

      return var

  def visitPlusExpr(self, node, lvalue=False):
    """Generate code for a unary plus expression"""
    # The result of a unary plus expression is not an lvalue
    if lvalue:
      return None

    return node.expr.accept(self)

  def visitNegExpr(self, node, lvalue=False):
    """Generate code for a negation expression"""
    # The result of a negation expression is not an lvalue
    if lvalue:
      return None

    # Allocate a temporary variable for the result
    var = next(self.varGen)
    # Generate code for the inner expression
    rvar = node.expr.accept(self)
    # Generate the instruction
    self.code.append(Neg(var, rvar))

    return var

  def visitNotExpr(self, node, lvalue=False):
    """Generate code for a bitwise NOT expression"""
    # The result of a bitwise NOT expression is not an lvalue
    if lvalue:
      return None

    # Allocate a temporary variable for the result
    var = next(self.varGen)
    # Generate code for the inner expression
    rvar = node.expr.accept(self)
    # Generate the instruction
    self.code.append(Not(var, rvar))

    return var

  def visitLogicNotExpr(self, node, lvalue=False):
    """Generate code for a logical NOT expression"""
    # The result of a bitwise NOT expression is not an lvalue
    if lvalue:
      return None

    # Allocate a temporary variable for the result
    var = next(self.varGen)
    # Generate code for the inner expression
    rvar = node.expr.accept(self)
    # Generate the instruction
    self.code.append(Equal(var, rvar, 0))

    return var

  def visitAssignExpr(self, node, lvalue=False):
    """Generate code for an assignment expression"""
    # The result of an assignment is not an lvalue
    if lvalue:
      return None

    # Generate code for the address of the variable
    addrVar = self.__genLValue(node.lexpr, "left operand of assignment")
    # Generate code for the right side of the assignment
    rvar = node.rexpr.accept(self)
    # Store the right side result in the lvalue
    self.code.append(Store(addrVar, rvar))

    return rvar

  def visitBinOpExpr(self, node, lvalue, inst):
    """Generate code for a binary operation expression"""
    # The result of a binary operation expression is not an lvalue
    if lvalue:
      return None

    # Allocate a temporary variable for the result
    var = next(self.varGen)
    # Generate code for the left side of the expression
    lvar = node.lexpr.accept(self)
    # Generate code for the right side of the expression
    rvar = node.rexpr.accept(self)
    # Generate the instruction
    self.code.append(inst(var, lvar, rvar))

    return var

  def visitLessThanExpr(self, node, lvalue=False):
    """Generate code for a less-than expression"""
    return self.visitBinOpExpr(node, lvalue, LessThan)

  def visitGreaterThanExpr(self, node, lvalue=False):
    """Generate code for a greater-than expression"""
    return self.visitBinOpExpr(node, lvalue, GreaterThan)

  def visitLessThanEqualExpr(self, node, lvalue=False):
    """Generate code for a less-than-or-equal-to expression"""
    return self.visitBinOpExpr(node, lvalue, LessThanEqual)

  def visitGreaterThanEqualExpr(self, node, lvalue=False):
    """Generate code for a greater-than-or-equal-to expression"""
    return self.visitBinOpExpr(node, lvalue, GreaterThanEqual)

  def visitEqualExpr(self, node, lvalue=False):
    """Generate code for an equal-to expression"""
    return self.visitBinOpExpr(node, lvalue, Equal)

  def visitNotEqualExpr(self, node, lvalue=False):
    """Generate code for a not-equal-to expression"""
    return self.visitBinOpExpr(node, lvalue, NotEqual)

  def visitAndExpr(self, node, lvalue=False):
    """Generate code for a bitwise AND expression"""
    return self.visitBinOpExpr(node, lvalue, And)

  def visitXorExpr(self, node, lvalue=False):
    """Generate code for a bitwise XOR expression"""
    return self.visitBinOpExpr(node, lvalue, Xor)

  def visitOrExpr(self, node, lvalue=False):
    """Generate code for a bitwise OR expression"""
    return self.visitBinOpExpr(node, lvalue, Or)

  def visitLogicOrExpr(self, node, lvalue=False):
    """Generate code for a logical OR expression"""
    # The result of a logical expression is not an lvalue
    if lvalue:
      return None

    # Allocate a temporary variable for the result
    var = next(self.varGen)
    # Allocate a label for the end of the right expression
    end_ = next(self.labelGen)

    # Generate code for the left expression
    lvar = node.lexpr.accept(self)
    # Convert to bool (0 or 1)
    self.code.append(NotEqual(var, lvar, 0))

    # Short-circuit if the result is true
    self.code.append(IfNotZeroJump(var, end_.id))

    # Generate code for the right expression
    rvar = node.rexpr.accept(self)
    # Convert to bool (0 or 1)
    self.code.append(NotEqual(var, rvar, 0))

    # Generate the end label
    self.code.append(Label(end_.id))

    return var

  def visitLogicAndExpr(self, node, lvalue=False):
    """Generate code for a logical AND expression"""
    # The result of a logical expression is not an lvalue
    if lvalue:
      return None

    # Allocate a temporary variable for the result
    var = next(self.varGen)
    # Allocate a label for the end of the right expression
    end_ = next(self.labelGen)

    # Generate code for the left expression
    lvar = node.lexpr.accept(self)
    # Convert to bool (0 or 1)
    self.code.append(NotEqual(var, lvar, 0))

    # Short-circuit if the result is false
    self.code.append(IfZeroJump(var, end_.id))

    # Generate code for the right expression
    rvar = node.rexpr.accept(self)
    # Convert to bool (0 or 1)
    self.code.append(NotEqual(var, rvar, 0))

    # Generate the end label
    self.code.append(Label(end_.id))

    return var

  def visitMulExpr(self, node, lvalue=False):
    """Generate code for a multiplication expression"""
    return self.visitBinOpExpr(node, lvalue, Mul)

  def visitDivExpr(self, node, lvalue=False):
    """Generate code for a division expression"""
    return self.visitBinOpExpr(node, lvalue, Div)

  def visitAddExpr(self, node, lvalue=False):
    """Generate code for an addition expression"""
    return self.visitBinOpExpr(node, lvalue, Add)

  def visitSubExpr(self, node, lvalue=False):
    """Generate code for a subtraction expression"""
    return self.visitBinOpExpr(node, lvalue, Sub)

  def visitCommaExpr(self, node, lvalue=False):
    """Generate code for a comma expression"""
    # The result of a comma expression is not an lvalue
    if lvalue:
      return None

    # Generate code for the left expression
    node.lexpr.accept(self)
    # Generate code for the right expression
    return node.rexpr.accept(self)

  def visitReturnStmt(self, node):
    """Generate code for a return statement"""
    # Generate code for the expression to return
    var = node.expr.accept(self)
    # Generate the function epilogue
    self.code.append(EndFunc(var))

  def visitIfStmt(self, node):
    """Generate code for an if statement"""
    # Allocate a label for the false part
    else_ = next(self.labelGen)
    # Allocate a label for the end of the statement
    end_ = next(self.labelGen)

    # Generate code for the conditional expression
    var = node.expr.accept(self)
    # Generate a jump to the else part on zero
    self.code.append(IfZeroJump(var, else_.id))
    # Generate code for the true part
    node.tstmt.accept(self)
    # Generate an instruction to jump to the end of the statement
    self.code.append(Jump(end_.id))
    # Generate a label for the false part
    self.code.append(Label(else_.id))
    # Generate code for the false part, if any
    if node.fstmt:
      node.fstmt.accept(self)
    # Generate a label for the end of the statement
    self.code.append(Label(end_.id))

  def visitWhileStmt(self, node):
    """Generate code for a while statement"""
    # Allocate a label for the beginning of the loop
    begin_ = next(self.labelGen)
    # Allocate a label for the end of the loop
    end_ = next(self.labelGen)
    # Generate a label for the beginning of the loop
    self.code.append(Label(begin_.id))
    # Generate code for the conditional expression
    var = node.expr.accept(self)
    # Generate an instruction to jump to the end of the loop on zero
    self.code.append(IfZeroJump(var, end_.id))
    # Generate code for the body of the loop
    node.stmt.accept(self)
    # Generate a jump to the beginning of the loop
    self.code.append(Jump(begin_.id))
    # Generate a label for the end of the loop
    self.code.append(Label(end_.id))

  def visitExprStmt(self, node):
    """Generate code for an expression statement"""
    if node.expr:
      node.expr.accept(self)

  def visitCompoundStmt(self, node):
    """Generate code for a compound statement"""
    # Enter a local environment
    self._pushEnv()
    # Define local variables in the local environment
    for decl in node.decls:
      decl.accept(self)
    # Generate code for the body statements
    for stmt in node.stmts:
      stmt.accept(self)
    # Exit the local environment
    self._popEnv()

  def visitDecl(self, node):
    """Generate code for a declaration"""
    # Generate code for initializers
    for init in node.inits:
      id_ = init.id

      # If this declaration is in the global scope, then add its name to the
      # environment
      if self.env.outer is None:
        self.env[id_] = GlobalVar(id_)
        # If this is not a function declaration, label it and reserve space
        if not (isinstance(init, syntree.FunDeclarator) or
          isinstance(init, syntree.KRFunDeclarator)):
          self.code.append(Label(id_))
          self.code.append(Word(UNINITIALIZED_WORD))
      # Otherwise, if this declaration is local, then map it to a temporary
      # variable
      else:
        self.env[id_] = next(self.varGen)

  def visitFunDef(self, node):
    """Generate code for a function definition"""
    # Add the function to the environment if it isn't already there
    id_ = node.declarator.id
    if id_ not in self.env:
      self.env[id_] = GlobalVar(id_)

    # Swap out the code buffer to grab the function code
    realCode = self.code
    self.code = []

    # Enter a local environment
    self._pushEnv()

    # Add the parameters to the environment (increasing in offset from right to
    # left)
    for param, off in zip(node.declarator.params,
      reversed(xrange(len(node.declarator.params)))):
      self.env[param.declarator.id] = ParamVar(off)

    # Generate the function code and count its local variables
    varOld = self.varGen.n
    node.stmt.accept(self)
    varNew = self.varGen.n

    # Exit the local environment
    self._popEnv()

    # Restore the code buffer
    funCode = self.code
    self.code = realCode

    # Generate the function label
    self.code.append(Label(node.declarator.id))
    # Generate the function prologue
    self.code.append(BeginFunc(varNew - varOld))
    # Insert the function code
    self.code.extend(funCode)

  def visitTranslationUnit(self, node):
    """Generate code for a translation unit"""
    # Generate code for each declaration
    for decl in node.decls:
      decl.accept(self)

    return self.code
