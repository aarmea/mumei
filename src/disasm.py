#!/usr/bin/env python

import itertools
import sys

import vm.bytecode as bytecode

def disasm(bc):
  it, it2 = itertools.tee(iter(bc))
  addr = 0
  while it:
    try:
      inst = bytecode.Instruction.decode(it2)
      print "%04X: %s" % (addr, inst)
      it = it2
      addr += len(bytecode.Instruction.encode(inst))
    except bytecode.InstructionError:
      word = next(it)
      print "%04X: %04X" % (addr, word)
      addr += 1
    except StopIteration:
      break

bc = eval(sys.stdin.read())
disasm(bc)
