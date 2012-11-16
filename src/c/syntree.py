"""
Syntax tree nodes for a subset of ANSI C

These types roughly correspond to the non-terminals in the C syntax
specification.
"""

import scanner

def visitable(cls):
  """A decorator for implementing the visitor pattern

  This decorator adds an accept function to the given class that calls the
  class-specific visit function on the visitor passed to the function.

  class Foo(...):
    def accept(self, visitor):
      return visitor.visitFoo(self)
  """

  def accept(self, visitor):
    # Grab the visitXXX function
    visit = getattr(visitor, "visit%s" % cls.__name__)
    return visit(self)

  # Add the accept function to the class
  setattr(cls, "accept", accept)
  return cls

# Built-in types

class Type(object):
  """The base class for all types"""

  def __repr__(self):
    return "%s()" % type(self).__name__

class IntType(Type):
  """An integer type"""

class LongType(Type):
  """A long integer type"""

class UIntType(Type):
  """An unsigned integer type"""

class ULongType(Type):
  """An unsigned long integer type"""

class FloatType(Type):
  """A single-precision floating-point type"""

class DoubleType(Type):
  """A double-precision floating-point type"""

class LongDoubleType(Type):
  """A long double floating-point type"""

class CharType(Type):
  """A character type"""

class WCharType(Type):
  """A wide character type"""

class PointerType(Type):
  """A pointer type"""

  def __init__(self, inner):
    self.inner = inner

  def __repr__(self):
    return "%s(inner=%r)" % (type(self).__name__, self.inner)

class FunType(Type):
  """A function type"""

  def __init__(self, params, ret):
    self.params = params
    self.ret = ret

  def __repr__(self):
    return ("%s(params=%r, ret=%r)" % (type(self).__name__, self.params,
      self.ret))

# External definitions

@visitable
class TranslationUnit(object):
  """A translation unit"""

  def __init__(self, decls):
    self.decls = decls

  def __repr__(self):
    return "%s(decls=%r)" % (type(self).__name__, self.decls)

class ExternalDecl(object):
  """An external declaration"""

@visitable
class FunDef(ExternalDecl):
  """A function definition"""

  def __init__(self, declarator, stmt):
    self.declarator = declarator
    self.stmt = stmt

  def __repr__(self):
    return ("%s(declarator=%r, stmt=%r)" % (type(self).__name__,
      self.declarator, self.stmt))

# Declarations

@visitable
class Decl(object):
  """A declaration"""

  def __init__(self, pos, inits):
    self.pos = pos
    self.inits = inits

  def __repr__(self):
    return "%s(pos=%r, inits=%r)" % (type(self).__name__, self.pos, self.inits)

class DeclSpec(object):
  """A declaration specifier"""

  def __init__(self, pos):
    self.pos = pos

  def __repr__(self):
    return "%s(pos=%r)" % (type(self).__name__, self.pos)

class InitDeclarator(object):
  """An initialization declarator"""

  def __init__(self, declarator, init):
    self.declarator = declarator
    self.init = init

  def __repr__(self):
    return ("%s(declarator=%r, init=%r)" % (type(self).__name__,
      self.declarator, self.init))

class StorageClassSpec(DeclSpec):
  """A storage class specifier"""

class TypedefStorageClassSpec(StorageClassSpec):
  """The typedef storage class"""

class ExternStorageClassSpec(StorageClassSpec):
  """The extern storage class"""

class StaticStorageClassSpec(StorageClassSpec):
  """The static storage class"""

class AutoStorageClassSpec(StorageClassSpec):
  """The auto storage class"""

class RegisterStorageClassSpec(StorageClassSpec):
  """The register storage class"""

class TypeSpec(DeclSpec):
  """A type specifier"""

class VoidTypeSpec(TypeSpec):
  """The void type specifier"""

class CharTypeSpec(TypeSpec):
  """The char type specifier"""

class ShortTypeSpec(TypeSpec):
  """The short type specifier"""

class IntTypeSpec(TypeSpec):
  """The int type specifier"""

class LongTypeSpec(TypeSpec):
  """The long type specifier"""

class FloatTypeSpec(TypeSpec):
  """The float type specifier"""

class DoubleTypeSpec(TypeSpec):
  """The double type specifier"""

class SignedTypeSpec(TypeSpec):
  """The signed type specifier"""

class UnsignedTypeSpec(TypeSpec):
  """The unsigned type specifier"""

class TypedefNameSpec(TypeSpec):
  """A typedef name type specifier"""

  def __init__(self, id_):
    self.id = id_

  def __repr__(self):
    return "%s(id_=%r)" % (type(self).__name__, self.id)

class StructOrUnionSpec(TypeSpec):
  """A struct or union type specifier"""

class InlineStructOrUnionSpec(StructOrUnionSpec):
  """A struct or union type specified inline"""

  def __init__(self, id_, decls):
    self.id = id_
    self.decls = decls

  def __repr__(self):
    return "%s(id_=%r, decls=%r)" % (type(self).__name__, self.id, self.decls)

class NamedStructOrUnionSpec(StructOrUnionSpec):
  """A struct or union type specified by name"""

  def __init__(self, id_):
    self.id = id_

  def __repr__(self):
    return "%s(id_=%r)" % (type(self).__name__, self.id)

class StructSpec(StructOrUnionSpec):
  """A struct type specifier"""

class InlineStructSpec(StructSpec, InlineStructOrUnionSpec):
  """A struct type specified inline"""

class NamedStructSpec(StructSpec, NamedStructOrUnionSpec):
  """A struct type specified by name"""

class UnionSpec(StructOrUnionSpec):
  """A union type specifier"""

class InlineUnionSpec(UnionSpec, InlineStructOrUnionSpec):
  """A union type specified inline"""

class NamedUnionSpec(UnionSpec, NamedStructOrUnionSpec):
  """A union type specified by name"""

class EnumSpec(TypeSpec):
  """An enumeration type specifier"""

class InlineEnumSpec(EnumSpec):
  """An enumeration type specified inline"""

  def __init__(self, id_, enums):
    self.id = id_
    self.enums = enums

  def __repr__(self):
    return "%s(id_=%r, enums=%r)" % (type(self).__name__, self.id, self.enums)

class NamedEnumSpec(EnumSpec):
  """An enumeration type specified by name"""

  def __init__(self, id_):
    self.id = id_

  def __repr__(self):
    return "%s(id_=%r)" % (type(self).__name__, self.id)

class Enumerator(object):
  """An item in an enumeration"""

  def __init__(self, id_, expr):
    self.id = id_
    self.expr = expr

  def __repr__(self):
    return "%s(id_=%r, expr=%r)" % (type(self).__name__, self.id, self.expr)

class TypeQual(DeclSpec):
  """A type qualifier"""

class ConstTypeQual(TypeQual):
  """A constant type qualifier"""

class VolatileTypeQual(TypeQual):
  """A volatile type qualifier"""

class Declarator(object):
  """A declarator"""

  def __init__(self):
    self.storageClassSpec = None
    self.type = None

  def applySpecs(self, storageClassSpec, typeSpec):
    self.storageClassSpec = storageClassSpec
    self.type = IntType() # XXX XXX XXX XXX everything is an int

  def __repr__(self):
    return ("%s(storageClassSpec=%r, type=%r)" % (type(self).__name__,
      self.storageClassSpec, self.typeSpec))

class PointerDeclarator(Declarator):
  """A pointer declarator"""

  def __init__(self, cv, inner):
    Declarator.__init__(self)
    self.const, self.volatile = cv
    self.inner = inner

  def __repr__(self):
    return ("%s(storageClassSpec=%r, type=%r, const=%r, volatile=%r, inner=%r)" %
      (type(self).__name__, self.storageClassSpec, self.type, self.const,
        self.volatile, self.inner))

  def applySpecs(self, storageClassSpec, typeSpec):
    self.storageClassSpec = storageClassSpec
    self.inner.applySpecs(None, typeSpec)
    self.type = PointerType(self.inner.type)

  id = property(lambda self: self.inner.id)

class DirectDeclarator(Declarator):
  """A direct declarator"""

  @classmethod
  def fromSuffixes(cls, direct, suffixes):
    """Construct a direct declarator from a declarator and a list of
    suffixes."""
    return reduce(lambda declarator, suffix:
      suffix.combine(declarator), suffixes, direct)

class NameDeclarator(DirectDeclarator):
  """A name declarator"""

  def __init__(self, id_):
    DirectDeclarator.__init__(self)
    self.id = id_

  def __repr__(self):
    return ("%s(storageClassSpec=%r, type=%r, id_=%r)" % (type(self).__name__,
      self.storageClassSpec, self.type, self.id))

class ArrayDeclarator(DirectDeclarator):
  """An array declarator"""

  def __init__(self, direct, expr):
    DirectDeclarator.__init__(self)
    self.direct = direct
    self.expr = expr

  def __repr__(self):
    return ("%s(storageClassSpec=%r, type=%r, direct=%r, expr=%r)" %
      (type(self).__name__, self.storageClassSpec, self.type, self.direct,
        self.expr))

  id = property(lambda self: self.direct.id)

class FunDeclarator(DirectDeclarator):
  """A function declarator"""

  def __init__(self, direct, params):
    DirectDeclarator.__init__(self)
    self.direct = direct
    self.params = params

  def __repr__(self):
    return ("%s(storageClassSpec=%r, type=%r, direct=%r, params=%r)" %
      (type(self).__name__, self.storageClassSpec, self.type, self.direct,
        self.params))

  def applySpecs(self, storageClassSpec, typeSpec):
    self.type = FunType([param.declarator.type for param in self.params],
      IntType()) # XXX all functions return int

  id = property(lambda self: self.direct.id)

class KRFunDeclarator(DirectDeclarator):
  """A K&R-style function declarator"""

  def __init__(self, direct, ids):
    DirectDeclarator.__init__(self)
    self.direct = direct
    self.ids = ids

  def __repr__(self):
    return ("%s(storageClassSpec=%r, type=%r, direct=%r, ids=%r)" %
      (type(self).__name__, self.storageClassSpec, self.type, self.direct,
        self.ids))

  id = property(lambda self: self.direct.id)

class DirectDeclaratorSuffix(object):
  """A direct declarator suffix"""

class ArrayDeclaratorSuffix(DirectDeclaratorSuffix):
  """An array declarator suffix"""

  def __init__(self, expr):
    self.expr = expr

  def __repr__(self):
    return "%s(expr=%r)" % (type(self).__name__, self.expr)

  def combine(self, direct):
    """Combine this suffix with a direct declarator, returning a new direct
    declarator."""
    return ArrayDeclarator(direct, self.expr)

class ParamDeclaratorSuffix(DirectDeclaratorSuffix):
  """A parameter list declarator suffix"""

  def __init__(self, params):
    self.params = params

  def __repr__(self):
    return "%s(params=%r)" % (type(self).__name__, self.params)

  def combine(self, direct):
    """Combine this suffix with a direct declarator, returning a new direct
    declarator."""
    return FunDeclarator(direct, self.params)

class KRDeclaratorSuffix(DirectDeclaratorSuffix):
  """A K&R-style names-only declarator suffix"""

  def __init__(self, ids):
    self.ids = ids

  def __repr__(self):
    return "%s(ids=%r)" % (type(self).__name__, self.ids)

  def combine(self, direct):
    """Combine this suffix with a direct declarator, returning a new direct
    declarator."""
    return KRFunDeclarator(direct, self.ids)

class ParamDecl(object):
  """A parameter declaration"""

  def __init__(self, declarator):
    self.declarator = declarator

  def __repr__(self):
    return "%s(declarator=%r)" % (type(self).__name__, self.declarator)

class Initializer(object):
  """An initializer"""

  def __init__(self, exprs):
    self.exprs = exprs

  def __repr__(self):
    return "%s(exprs=%r)" % (type(self).__name__, self.exprs)

# Statements

class Stmt(object):
  """A statement"""

  def __repr__(self):
    return "%s()" % type(self).__name__

class LabeledStmt(Stmt):
  """A labeled statement"""

  # XXX Not implemented

@visitable
class CompoundStmt(Stmt):
  """A compound statement"""

  def __init__(self, decls, stmts):
    self.decls = decls
    self.stmts = stmts

  def __repr__(self):
    return ("%s(decls=%r, stmts=%r)" % (type(self).__name__, self.decls,
      self.stmts))

@visitable
class ExprStmt(Stmt):
  """An expression statement"""

  def __init__(self, expr):
    self.expr = expr

  def __repr__(self):
    return "%s(expr=%r)" % (type(self).__name__, self.expr)

class SelectionStmt(Stmt):
  """A selection statement"""

@visitable
class IfStmt(SelectionStmt):
  """An if statement"""

  def __init__(self, expr, tstmt, fstmt):
    self.expr = expr
    self.tstmt = tstmt
    self.fstmt = fstmt

  def __repr__(self):
    return "%s(expr=%r, tstmt=%r, fstmt=%r)" % (type(self).__name__,
      self.expr, self.tstmt, self.fstmt)

# XXX switch not implemented

class IterationStmt(Stmt):
  """An iteration statement"""

@visitable
class WhileStmt(IterationStmt):
  """A while statement"""

  def __init__(self, expr, stmt):
    self.expr = expr
    self.stmt = stmt

  def __repr__(self):
    return "%s(expr=%r, stmt=%r)" % (type(self).__name__, self.expr,
      self.stmt)

# XXX do/for not implemented

class JumpStmt(Stmt):
  """A jump statement"""

class GoToStmt(JumpStmt):
  """A goto statement"""

  def __init__(self, id_):
    self.id = id_

  def __repr__(self):
    return "%s(id_=%r)" % (type(self).__name__, self.id_)

class ContinueStmt(JumpStmt):
  """A continue statement"""

class BreakStmt(JumpStmt):
  """A break statement"""

@visitable
class ReturnStmt(JumpStmt):
  """A return statement"""

  def __init__(self, expr):
    self.expr = expr

  def __repr__(self):
    return "%s(expr=%r)" % (type(self).__name__, self.expr)

# Expressions

class Expr(object):
  """An expression"""

class CommaExpr(Expr):
  """A comma expression"""

  def __init__(self, lexpr, rexpr):
    self.lexpr = lexpr
    self.rexpr = rexpr

  def __repr__(self):
    return ("%s(lexpr=%r, rexpr=%r)" % (type(self).__name__, self.lexpr,
      self.rexpr))

@visitable
class AssignExpr(Expr):
  """An assignment expression"""

  def __init__(self, lexpr, op, rexpr):
    self.lexpr = lexpr
    self.op = op
    self.rexpr = rexpr

  def __repr__(self):
    return ("%s(op=%r, lexpr=%r, rexpr=%r" % (type(self).__name__, self.op,
      self.lexpr, self.rexpr))

# XXX More expressions

@visitable
class LessThanExpr(Expr):
  """A less-than expression"""

  def __init__(self, lexpr, rexpr):
    self.lexpr = lexpr
    self.rexpr = rexpr

  def __repr__(self):
    return ("%s(lexpr=%r, rexpr=%r)" % (type(self).__name__, self.lexpr,
      self.rexpr))

@visitable
class AddExpr(Expr):
  """An addition expression"""

  def __init__(self, lexpr, rexpr):
    self.lexpr = lexpr
    self.rexpr = rexpr

  def __repr__(self):
    return ("%s(lexpr=%r, rexpr=%r)" % (type(self).__name__, self.lexpr,
      self.rexpr))

class UnaryExpr(Expr):
  """A unary expression"""

@visitable
class DerefExpr(UnaryExpr):
  """A dereference expression"""

  def __init__(self, expr):
    self.expr = expr

  def __repr__(self):
    return "%s(expr=%r)" % (type(self).__name__, self.expr)

class PostfixExpr(Expr):
  """A postfix expression"""

@visitable
class CallExpr(PostfixExpr):
  """A function call expression"""

  def __init__(self, funExpr, argExprs):
    self.funExpr = funExpr
    self.argExprs = argExprs

  def __repr__(self):
    return ("%s(funExpr=%r, argExprs=%r)" % (type(self).__name__, self.funExpr,
      self.argExprs))

class PrimaryExpr(Expr):
  """A primary expression"""

@visitable
class VarExpr(PrimaryExpr):
  """A variable expression"""

  def __init__(self, id_):
    self.id = id_

  def __repr__(self):
    return "%s(id_=%r)" % (type(self).__name__, self.id)

@visitable
class ConstExpr(PrimaryExpr):
  """A constant expression"""

  def __init__(self, type_, val):
    self.type = type_
    self.val = val

  def __repr__(self):
    return "%s(type_=%r, val=%r)" % (type(self).__name__, self.type, self.val)

class StringLiteralExpr(PrimaryExpr):
  """A string literal expression"""

  def __init__(self, val):
    self.val = val

  def __repr__(self):
    return "%s(val=%r)" % (type(self).__name__, self.val)
