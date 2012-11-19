#!/usr/bin/env python

import itertools
import sys

from c.error import CompileError
import c.scanner as scanner
import c.parser as parser
import c.tacgen as tacgen
import vm.bytecode as bytecode
import vm.tactrans as tactrans

def disasm(bc):
  it, it2 = itertools.tee(iter(bc))
  while it:
    try:
      yield str(bytecode.Instruction.decode(it2))
      it = it2
    except bytecode.InstructionError:
      yield str("%04X" % next(it))

try:
  warnings = []
  ts = list(scanner.tokensAndWarnings(scanner.scan(sys.stdin.read()), warnings))
  print "TOKENS"
  print ts
  print
  for warn in warnings:
    print "WARNING:", warn
  print
  ast = parser.parse(ts)
  print "SYNTAX TREE"
  print ast
  print
  tac = ast.accept(tacgen.TACGenerator())
  print "THREE-ADDRESS CODE"
  print tac
  print
  bc, _ = tactrans.translate(tac)
  print "BYTECODE"
  print bc
  print
  print "DISASSEMBLY"
  print list(disasm(bc))
except CompileError, e:
  print
  print "ERROR:", e
