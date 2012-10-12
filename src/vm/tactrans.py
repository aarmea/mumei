"""
A translator from three-address code to bytecode
"""

import itertools

import bytecode
import threeaddr.threeaddr as threeaddr

def _negateWord(val):
  """Negate a processor word."""
  return -val & bytecode.Processor.WORD_MASK

def _localOperand(env, var):
  """Return an operand for a local variable."""
  off = env[var] + 1
  return bytecode.IndRegOffOperand(bytecode.Processor.REG_X3, _negateWord(off))

def translate(tac):
  """Translate a three-address code sequence to a bytecode sequence."""
  bc = []

  # XXX Split TAC into functions

  # XXX Implement register allocation

  nextLocal = 0
  env = {}

  for inst in tac:
    if isinstance(inst, threeaddr.BeginFunc):
      # Save the stack pointer
      bc.append(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_X3),
          bytecode.RegOperand(bytecode.Processor.REG_SP)
        )
      )

      # Reserve stack space for local variables
      if inst.nlocals:
        bc.append(
          bytecode.Add(
            bytecode.RegOperand(bytecode.Processor.REG_SP),
            bytecode.ImmOperand(_negateWord(inst.nlocals))
          )
        )

    elif isinstance(inst, threeaddr.Assign):
      if not inst.dst in env:
        env[inst.dst] = nextLocal
        nextLocal += 1

      bc.append(
        bytecode.Set(
          _localOperand(env, inst.dst),
          bytecode.ImmOperand(inst.src)
        )
      )

    elif isinstance(inst, threeaddr.Add):
      if not inst.dst in env:
        env[inst.dst] = nextLocal
        nextLocal += 1

      bc.append(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_X0),
          _localOperand(env, inst.srca)
        )
      )
      bc.append(
        bytecode.Add(
          bytecode.RegOperand(bytecode.Processor.REG_X0),
          _localOperand(env, inst.srcb)
        )
      )
      bc.append(
        bytecode.Set(
          _localOperand(env, inst.dst),
          bytecode.RegOperand(bytecode.Processor.REG_X0)
        )
      )

    elif isinstance(inst, threeaddr.Return):
      bc.append(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_X0),
          _localOperand(env, inst.src)
        )
      )

    elif isinstance(inst, threeaddr.EndFunc):
      # Restore the stack pointer
      bc.append(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_SP),
          bytecode.RegOperand(bytecode.Processor.REG_X3)
        )
      )

      # Pop the return address and jump to it
      bc.append(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_IP),
          bytecode.IndIncRegOperand(bytecode.Processor.REG_SP)
        )
      )

    else:
      raise NotImplementedError(inst) # XXX

  return list(itertools.chain(*(inst.encode() for inst in bc)))
