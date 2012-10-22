"""
A translator from three-address code to bytecode
"""

import bytecode
import threeaddr.threeaddr as threeaddr

PATCH_WORD = 0xCCCC

def _negateWord(val):
  """Negate a processor word."""
  return -val & bytecode.Processor.WORD_MASK

def _reserveLocal(localVars, localOff, var):
  """Reserve stack space for a local variable if necessary."""
  if not var in localVars:
    localVars[var] = localOff
    localOff += 1
  return localOff

def _getOperand(localVars, patches, patchOff, var):
  """Return an operand for the given variable name, adding an entry to the
  patch list as necessary."""
  if var in localVars:
    # Look up the variable in the local environment
    off = localVars[var] + 1
    return (bytecode.IndRegOffOperand(bytecode.Processor.REG_X3,
      _negateWord(off)), patchOff + 1)
  else:
    # Generate a patch to be resolved later
    patches.append((var, patchOff + 1))
    return (bytecode.IndImmOperand(PATCH_WORD), patchOff + 1)

def _getTarget(patches, patchOff, label):
  """Return an operand for the given jump target, adding an entry to the patch
  list."""
  patches.append((label, patchOff + 1))
  return bytecode.ImmOperand(0)

def translate(tac):
  """Translate a three-address code sequence to a bytecode sequence."""
  bc = []

  def appendInst(inst):
    """Encode an instruction and append the resulting bytecode."""
    bc.extend(inst.encode())

  # Second pass information
  labels = {}
  patches = []

  # XXX Implement register allocation

  for inst in tac:
    if isinstance(inst, threeaddr.Label):
      # Add the label name and current offset to the label map
      labels[inst.name] = len(bc)

    elif isinstance(inst, threeaddr.Word):
      # Emit a word directly
      bc.append(inst.val)

    elif isinstance(inst, threeaddr.BeginFunc):
      # Reset local variables
      localVars = {}
      localOff = 0

      # Save the stack pointer
      appendInst(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_X3),
          bytecode.RegOperand(bytecode.Processor.REG_SP)
        )
      )

      # Reserve stack space for local variables
      if inst.nwords:
        appendInst(
          bytecode.Add(
            bytecode.RegOperand(bytecode.Processor.REG_SP),
            bytecode.ImmOperand(_negateWord(inst.nwords))
          )
        )

    elif isinstance(inst, threeaddr.EndFunc):
      # Set the return value
      op, _ = _getOperand(localVars, patches, len(bc), inst.ret)
      appendInst(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_X0),
          op
        )
      )

      # Restore the stack pointer
      appendInst(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_SP),
          bytecode.RegOperand(bytecode.Processor.REG_X3)
        )
      )

      # Pop the return address and jump to it
      appendInst(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_IP),
          bytecode.IndIncRegOperand(bytecode.Processor.REG_SP)
        )
      )

    elif isinstance(inst, threeaddr.Assign):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      dstOp, patchOff = _getOperand(localVars, patches, len(bc), inst.dst)
      if isinstance(inst.src, int):
        srcOp = bytecode.ImmOperand(inst.src)
      else:
        srcOp, _ = _getOperand(localVars, patches, patchOff, inst.src)
      appendInst(bytecode.Set(dstOp, srcOp))

    elif isinstance(inst, threeaddr.Add):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      op, _ = _getOperand(localVars, patches, len(bc), inst.srca)
      appendInst(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_X0),
          op
        )
      )
      op, _ = _getOperand(localVars, patches, len(bc), inst.srcb)
      appendInst(
        bytecode.Add(
          bytecode.RegOperand(bytecode.Processor.REG_X0),
          op
        )
      )
      op, _ = _getOperand(localVars, patches, len(bc),  inst.dst)
      appendInst(
        bytecode.Set(
          op,
          bytecode.RegOperand(bytecode.Processor.REG_X0)
        )
      )

    elif isinstance(inst, threeaddr.Jump):
      appendInst(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_IP),
          _getTarget(patches, len(bc), inst.label)
        )
      )

    elif isinstance(inst, threeaddr.IfZeroJump):
      # Set the flags register
      op, _ = _getOperand(localVars, patches, len(bc), inst.src)
      appendInst(
        bytecode.Or(
          bytecode.ShortImmOperand(0),
          op
        )
      )

      # Check the flags register
      appendInst(
        bytecode.If(
          bytecode.RegOperand(bytecode.Processor.REG_FL),
          bytecode.ShortImmOperand(bytecode.Processor.FLAG_ZERO)
        )
      )

      # Jump to the target
      appendInst(
        bytecode.Set(
          bytecode.RegOperand(bytecode.Processor.REG_IP),
          _getTarget(patches, len(bc), inst.label)
        )
      )

    else:
      raise NotImplementedError(inst) # XXX

  # Resolve patches
  for label, off in patches:
    bc[off] = labels[label]

  return bc
