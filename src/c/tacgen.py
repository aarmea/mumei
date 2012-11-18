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

  def visitCallExpr(self, node, lvalue=False):
    """Generate code for a function call expression"""
    # The result of a call is not an lvalue
    if lvalue:
      return None

    # Allocate a temporary variable for the return value
    var = next(self.varGen)
    # Generate code to grab the function address
    funAddrVar = node.funExpr.accept(self, True)

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

  def visitAssignExpr(self, node, lvalue=False):
    """Generate code for an assignment expression"""
    # The result of an assignment is not an lvalue
    if lvalue:
      return None

    # Generate code for the address of the variable
    addrVar = node.lexpr.accept(self, True)
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

  def visitAddExpr(self, node, lvalue=False):
    """Generate code for an addition expression"""
    return self.visitBinOpExpr(node, lvalue, Add)

  def visitSubExpr(self, node, lvalue=False):
    """Generate code for a subtraction expression"""
    return self.visitBinOpExpr(node, lvalue, Sub)

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
        self.env[init.id] = GlobalVar(id_)
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
