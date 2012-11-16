#!/usr/bin/env python
"""
A virtual machine command-line interface
"""

import re
import select
import sys

import c.error as error
import c.scanner as scanner
import c.parser as parser
import c.tacgen as tacgen
import vm.tactrans as tactrans
import vm.bytecode as bytecode

helpstr = """Command prompt:
 >>> 00: asm SET IP, $0
     ^   ^   ^   ^   ^-- short-form immediate value (hex)
     |   |   |   `-- register 
     |   |   `-- instruction
     |   `-- command
     `-- cursor location in memory (hex)

 >>> 08: comp int f(int x) { return x + 9; }
              ^-- C program

Commands:
 ?, help         Display this message
 a, asm  <inst>  Assemble an instruction and store the resulting bytecode at
                  the current location
 c, comp <prog>  Compile a C program and store the resulting bytecode
                  at the current location
    dis  <addr>  Disassemble the instruction at the given address (hex)
 d, dump         Dump the current processor state
 g, go   <addr>  Set the current location to the given memory address (hex)
 p, poke <val>   Store the given value at the current location (hex)
    reg  <r> <v> Set a register to the given value (hex)
 r, run          Execute instructions until stopped
 s, step         Execute the next instruction
 q, quit         Quit
"""

class AssembleError(Exception):
  pass

class CompileError(Exception):
  pass

def readReg(s):
  """Return the register code for a register name."""
  return getattr(bytecode.Processor, "REG_%s" % s.upper())

def readop(s):
  """Construct an operand from an operand string."""
  try:
    mo = re.match(r"^[0-9A-F]+$", s, re.I)
    if mo:
      return bytecode.ImmOperand(int(s, 16))
    mo = re.match(r"^\w+$", s)
    if mo:
      return bytecode.RegOperand(readReg(s))
    mo = re.match(r"^(\w+)\s*\+\s*([0-9A-F]+)$", s, re.I)
    if mo:
      return bytecode.RegOffOperand(readReg(mo.group(1)),
        int(mo.group(2), 16))
    mo = re.match(r"^\[([0-9A-F]+)\]$", s, re.I)
    if mo:
      return bytecode.IndImmOperand(int(mo.group(1), 16))
    mo = re.match(r"^\[(\w+)\]$", s)
    if mo:
      return bytecode.IndRegOperand(readReg(mo.group(1)))
    mo = re.match(r"^\[(\w+)\s*\+\s*([0-9A-F]+)\]$", s, re.I)
    if mo:
      return bytecode.IndRegOffOperand(readReg(mo.group(1)),
        int(mo.group(2), 16))
    mo = re.match(r"^\[(\w+)\+\+\]$", s)
    if mo:
      return bytecode.IndIncRegOperand(readReg(mo.group(1)))
    mo = re.match(r"^\[--(\w+)\]$", s)
    if mo:
      return bytecode.IndDecRegOperand(readReg(mo.group(1)))
    mo = re.match(r"^\$(-?[0-9A-F]+)$", s, re.I)
    if mo:
      return bytecode.ShortImmOperand(int(mo.group(1), 16))
  except (AttributeError, bytecode.InstructionError, ValueError):
    pass
  raise AssembleError("invalid operand: %s" % s)

def asm(s):
  """Assemble an instruction string and return its instruction words."""
  opre = (r"(\w+|\w+\s*\+\s*\w+|\[\w+\]|\[\w+\s*\+\s*\w+\]"
    r"|\[\w+\+\+\]|\[--\w+\]|\$-?[0-9A-F]+)")
  instre = r"^\s*(\w+)\s+" + opre + r"\s*(?:,|\s+)\s*" + opre + "\s*$"

  mo = re.match(instre, s, re.I)
  if not mo:
    raise AssembleError("syntax error")

  try:
    opcls = bytecode.Instruction.fromMnemonic(mo.group(1))
  except KeyError:
    raise AssembleError("unknown instruction")

  opa = readop(mo.group(2))
  opb = readop(mo.group(3))

  return opcls(opa, opb).encode()

def disasm(proc, addr):
  """Disassemble the instruction at the given address."""
  seq = proc.memSeq(addr)
  return str(bytecode.Instruction.decode(seq))

def comp(s):
  """Compile a C program and return its instruction words."""
  try:
    ts = list(scanner.tokens(scanner.scan(s)))
    ast = parser.parse(ts)
    tac = ast.accept(tacgen.TACGenerator())
    return tactrans.translate(tac)
  except scanner.ScanError, e:
    raise CompileError("scan error: %s" % e)
  except parser.ParseError, e:
    raise CompileError("syntax error: %s" % e)
  except error.CompileError, e:
    raise CompileError("compile error: %s" % e)
  except NotImplementedError, e:
    raise CompileError("not implemented: %s" % e)

def dump(proc):
  """Dump a processor's state."""
  width = 8
  ip = proc.getReg(proc.REG_IP)

  print "MEMORY:",
  for addr in xrange(0, proc.memWords):
    if not (addr % width):
      print "\n%02X:" % addr,

    # Turn off the leading space before printing
    sys.stdout.softspace = 0
    print "%s%04X" % ('>' if addr == ip else ' ', proc.getMem(addr)),

  print
  print
  print "REGISTERS:"
  print " X0 %04X   X2 %04X        FL %04X   SP %04X" % \
    (proc.getReg(proc.REG_X0), proc.getReg(proc.REG_X2),
     proc.getReg(proc.REG_FL), proc.getReg(proc.REG_SP))
  print " X1 %04X   X3 %04X                  IP %04X" % \
    (proc.getReg(proc.REG_X1), proc.getReg(proc.REG_X3),
     proc.getReg(proc.REG_IP))
  print

  print "CYCLE: %d" % proc.cycle
  try:
    inst = disasm(proc, proc.getReg(proc.REG_IP))
  except bytecode.InstructionError:
    inst = "(invalid)"
  print "NEXT INSTRUCTION: %s" % inst

def main():
  proc = bytecode.Processor(memWords=256)
  cursor = 0

  try:
    while True:
      line = raw_input(">>> %02X: " % cursor)
      parts = line.split(None, 1)

      if parts:
        cmd = parts[0]
        lcmd = cmd.lower()

        if lcmd == "?" or lcmd == "help":
          print helpstr
        elif lcmd == "a" or lcmd == "asm":
          if len(parts) != 2:
            print "Usage: asm <instruction>"
          else:
            addr = cursor
            try:
              words = asm(parts[1])
              for word in words:
                proc.setMem(cursor, word)
                cursor = (cursor + 1) % proc.memWords
              print "Assembled %d words at %02X" % (len(words), addr)
            except AssembleError, e:
              print "Assembly error: %s" % e
        elif lcmd == "c" or lcmd == "comp":
          if len(parts) != 2:
            print "Usage: comp <program>"
          else:
            addr = cursor
            try:
              words = comp(parts[1])
              for word in words:
                proc.setMem(cursor, word)
                cursor = (cursor + 1) % proc.memWords
              print "Compiled %d words at %02X" % (len(words), addr)
            except CompileError, e:
              print "Compile error: %s" % e
        elif lcmd == "dis":
          parts = line.split()
          if len(parts) != 2:
            print "Usage: dis <address>"
          else:
            addr = int(parts[1], 16)
            try:
              print "Disassembly: %02X: %s" % (addr, disasm(proc, addr))
            except bytecode.InstructionError, e:
              print "Disassembly: %s" % e
        elif lcmd == "d" or lcmd == "dump":
          dump(proc)
        elif lcmd == "g" or lcmd == "go":
          parts = line.split()
          if len(parts) != 2:
            print "Usage: go <address>"
          else:
            addr = int(parts[1], 16)
            if addr >= 0 and addr < proc.memWords:
              cursor = addr
            else:
              print "Memory address out of bounds"
        elif lcmd == "p" or lcmd == "poke":
          parts = line.split()
          if len(parts) != 2:
            print "Usage: poke <value>"
          else:
            try:
              val = int(parts[1], 16)
            except ValueError:
              print "Invalid value"
            proc.setMem(cursor, val)
            cursor = (cursor + 1) % proc.memWords
        elif lcmd == "reg":
          parts = line.split()
          if len(parts) != 3:
            print "Usage: reg <register> <value>"
          else:
            try:
              reg = readReg(parts[1])
              val = int(parts[2], 16)
              proc.setReg(reg, val)
            except AttributeError:
              print "Invalid register"
            except ValueError:
              print "Invalid value"
        elif lcmd == "r" or lcmd == "run":
          print "Running..."
          try:
            while True:
              print
              proc.step()
              dump(proc)
              rlist, _, _ = select.select([sys.stdin], [], [], 0.5)
              if rlist:
                sys.stdin.readline()
                break
          except bytecode.ProcessorError, e:
            print "Processor: %s" % e
          print "Stopped"
        elif lcmd == "s" or lcmd == "step":
          try:
            proc.step()
            dump(proc)
          except bytecode.ProcessorError, e:
            print "Processor: %s" % e
        elif lcmd == "q" or lcmd == "quit":
          break
        else:
          print "Unrecognized command:", cmd

  except EOFError:
    print

if __name__ == "__main__":
  main()
