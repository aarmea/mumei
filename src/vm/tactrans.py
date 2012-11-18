"""
A translator from three-address code to bytecode
"""

from bytecode import *

# Some threeaddr classes have naming conflicts with the bytecode module
# (e.g. Add), so this has to be a named import.
import threeaddr.threeaddr as threeaddr

PATCH_WORD = 0xAAAA
"""A placeholder value for patch locations"""

def _negateWord(val):
  """Negate a processor word."""
  return -val & Processor.WORD_MASK

def _reserveLocal(localVars, localOff, var):
  """Reserve stack space for a local variable if necessary."""
  if isinstance(var, threeaddr.LocalVar):
    if not var.id in localVars:
      localVars[var.id] = localOff
      localOff += 1

  return localOff

def _getOperand(localVars, patches, patchOff, var):
  """Return an operand for the given variable, adding an entry to the patch
  list as necessary."""
  if isinstance(var, int):
    # Emit the constant directly
    return (ImmOperand(var), patchOff + 1)
  elif isinstance(var, str):
    # Generate a patch for the given label
    patches.append((var, patchOff + 1))
    return (ImmOperand(PATCH_WORD), patchOff + 1)
  elif isinstance(var, threeaddr.ParamVar):
    # Get the variable on the stack
    return (IndRegOffOperand(Processor.REG_X3, var.off + 2),
      patchOff + 1)
  elif isinstance(var, threeaddr.LocalVar):
    # Look up the variable in the local environment
    off = localVars[var.id] + 1
    return (IndRegOffOperand(Processor.REG_X3,
      _negateWord(off)), patchOff + 1)
  elif isinstance(var, threeaddr.GlobalVar):
    # Generate a patch to be resolved later
    patches.append((var.id, patchOff + 1))
    return (IndImmOperand(PATCH_WORD), patchOff + 1)
  else:
    # Not a valid variable type
    assert False

def _getAddrOperand(localVars, patches, patchOff, var):
  """Return an operand for the address of the given variable, adding an entry to
  the patch list as necessary."""
  if isinstance(var, int):
    # Emit the constant directly
    return (ImmOperand(var), patchOff + 1)
  elif isinstance(var, str):
    # Generate a patch for the given label
    patches.append((var, patchOff + 1))
    return (ImmOperand(PATCH_WORD), patchOff + 1)
  elif isinstance(var, threeaddr.ParamVar):
    # Get the variable on the stack
    return (RegOffOperand(Processor.REG_X3, var.off + 2),
      patchOff + 1)
  elif isinstance(var, threeaddr.LocalVar):
    # Look up the variable in the local environment
    off = localVars[var.id] + 1
    return (RegOffOperand(Processor.REG_X3, _negateWord(off)),
      patchOff + 1)
  elif isinstance(var, threeaddr.GlobalVar):
    # Generate a patch to be resolved later
    patches.append((var.id, patchOff + 1))
    return (ImmOperand(PATCH_WORD), patchOff + 1)
  else:
    # Not a valid variable
    assert False

def translate(tac):
  """Translate a three-address code sequence to a bytecode sequence, returning
  the bytecode and a dictionary of labels for external linkage."""
  code = []

  def appendInst(inst):
    """Encode an instruction and append the resulting bytecode."""
    code.extend(inst.encode())

  # Second pass information
  labels = {}
  patches = []

  # XXX Implement register allocation

  for inst in tac:
    if isinstance(inst, threeaddr.Label):
      # Add the label name and current offset to the label map
      labels[inst.id] = len(code)

    elif isinstance(inst, threeaddr.Word):
      # Emit a word directly
      code.append(inst.val)

    elif isinstance(inst, threeaddr.BeginFunc):
      # Reset local variables
      localVars = {}
      localOff = 0

      # Save the caller's base pointer
      appendInst(
        Set(IndDecRegOperand(Processor.REG_SP), RegOperand(Processor.REG_X3))
      )

      # Save the stack pointer
      appendInst(
        Set(RegOperand(Processor.REG_X3), RegOperand(Processor.REG_SP))
      )

      # Reserve stack space for local variables
      if inst.nwords:
        appendInst(
          Add(
            RegOperand(Processor.REG_SP),
            ImmOperand(_negateWord(inst.nwords))
          )
        )

    elif isinstance(inst, threeaddr.EndFunc):
      retOp, _ = _getOperand(localVars, patches, len(code), inst.ret)

      # Set the return value
      appendInst(
        Set(RegOperand(Processor.REG_X0), retOp)
      )

      # Restore the stack pointer
      appendInst(
        Set(RegOperand(Processor.REG_SP), RegOperand(Processor.REG_X3))
      )

      # Restore the base pointer
      appendInst(
        Set(RegOperand(Processor.REG_X3), IndIncRegOperand(Processor.REG_SP))
      )

      # Pop the return address and jump to it
      appendInst(
        Set(RegOperand(Processor.REG_IP), IndIncRegOperand(Processor.REG_SP))
      )

    elif isinstance(inst, threeaddr.Assign):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      dstOp, patchOff = _getOperand(localVars, patches, len(code), inst.dst)
      srcOp, _ = _getOperand(localVars, patches, patchOff, inst.src)
      appendInst(Set(dstOp, srcOp))

    elif isinstance(inst, threeaddr.Load):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      srcOp, _ = _getOperand(localVars, patches, len(code), inst.src)

      # Load the source address into a register
      appendInst(
        Set(RegOperand(Processor.REG_X0), srcOp)
      )

      dstOp, patchOff = _getOperand(localVars, patches, len(code), inst.dst)

      # Read the value at the source address into the destination
      appendInst(
        Set(dstOp, IndRegOperand(Processor.REG_X0))
      )

    elif isinstance(inst, threeaddr.AddressOf):
      localOff = _reserveLocal(localVars, localOff, inst.dst)
      localOff = _reserveLocal(localVars, localOff, inst.src)

      dstOp, patchOff = _getOperand(localVars, patches, len(code), inst.dst)
      srcOp, _ = _getAddrOperand(localVars, patches, patchOff, inst.src)

      # Set the destination variable to the address of the source variable
      appendInst(Set(dstOp, srcOp))

    elif isinstance(inst, threeaddr.Store):
      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)

      # Load the destination address into a register
      appendInst(
        Set(RegOperand(Processor.REG_X0), dstOp)
      )

      srcOp, _ = _getOperand(localVars, patches, len(code), inst.src)

      # Store the source value at the destination address
      appendInst(
        Set(IndRegOperand(Processor.REG_X0), srcOp)
      )

    elif isinstance(inst, threeaddr.PushParam):
      srcOp, _ = _getOperand(localVars, patches, len(code), inst.src)

      # Push the source value on the stack
      appendInst(
        Set(IndDecRegOperand(Processor.REG_SP), srcOp)
      )

    elif isinstance(inst, threeaddr.PopParams):
      # Remove nwords values from the stack
      appendInst(
        Add(RegOperand(Processor.REG_SP), ImmOperand(inst.nwords))
      )

    elif isinstance(inst, threeaddr.Call):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      targetOp, _ = _getOperand(localVars, patches, len(code), inst.target)

      # Generate a label name and patch for the return address
      retLabel = "#ret%x" % len(code)
      patches.append((retLabel, len(code) + 1))

      # Push the return address on the stack
      appendInst(
        Set(IndDecRegOperand(Processor.REG_SP), ImmOperand(PATCH_WORD))
      )

      # Jump to the given address
      appendInst(
        Set(RegOperand(Processor.REG_IP), targetOp)
      )

      # Label the return address
      labels[retLabel] = len(code)

      # Get the return value
      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)
      appendInst(
        Set(dstOp, RegOperand(Processor.REG_X0))
      )

    elif isinstance(inst, threeaddr.LessThan):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      srcOpA, patchOff = _getOperand(localVars, patches, len(code), inst.srca)
      srcOpB, _ = _getOperand(localVars, patches, patchOff, inst.srcb)

      # Subtract the second variable from the first variable
      appendInst(
        Sub(srcOpA, srcOpB)
      )

      # Mask the less-than flag in the flags register
      appendInst(
        And(RegOperand(Processor.REG_FL), ShortImmOperand(Processor.FLAG_LESS))
      )

      # Copy the flags temporarily
      # XXX The flags register should probably be updated if it isn't the
      # destination operand of an instruction.
      appendInst(
        Set(RegOperand(Processor.REG_X0), RegOperand(Processor.REG_FL))
      )

      # Check whether the flags are non-zero
      appendInst(
        Xor(RegOperand(Processor.REG_X0), ShortImmOperand(Processor.FLAG_LESS))
      )

      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)

      # Copy the flags register to the destination variable
      appendInst(
        Set(dstOp, RegOperand(Processor.REG_FL))
      )

    elif isinstance(inst, threeaddr.GreaterThan):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      srcOpA, patchOff = _getOperand(localVars, patches, len(code), inst.srca)
      srcOpB, _ = _getOperand(localVars, patches, patchOff, inst.srcb)

      # Subtract the second variable from the first variable
      appendInst(
        Sub(srcOpA, srcOpB)
      )

      # Mask the less-than and zero flags in the flags register
      appendInst(
        And(
          RegOperand(Processor.REG_FL),
          ShortImmOperand(Processor.FLAG_LESS | Processor.FLAG_ZERO)
        )
      )

      # Copy the flags temporarily
      # XXX The flags register should probably be updated if it isn't the
      # destination operand of an instruction.
      appendInst(
        Set(RegOperand(Processor.REG_X0), RegOperand(Processor.REG_FL))
      )

      # Check whether the flags are zero
      appendInst(
        Or(RegOperand(Processor.REG_X0), ShortImmOperand(0))
      )

      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)

      # Copy the flags register to the destination variable
      appendInst(
        Set(dstOp, RegOperand(Processor.REG_FL))
      )

    elif isinstance(inst, threeaddr.LessThanEqual):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      srcOpA, patchOff = _getOperand(localVars, patches, len(code), inst.srca)
      srcOpB, _ = _getOperand(localVars, patches, patchOff, inst.srcb)

      # Subtract the second variable from the first variable
      appendInst(
        Sub(srcOpA, srcOpB)
      )

      # Mask the less-than flag in the flags register
      appendInst(
        And(RegOperand(Processor.REG_FL), ShortImmOperand(Processor.FLAG_LESS))
      )

      # Copy the flags temporarily
      # XXX The flags register should probably be updated if it isn't the
      # destination operand of an instruction.
      appendInst(
        Set(RegOperand(Processor.REG_X0), RegOperand(Processor.REG_FL))
      )

      # Check whether the flags are non-zero
      appendInst(
        Xor(RegOperand(Processor.REG_X0), ShortImmOperand(Processor.FLAG_LESS))
      )

      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)

      # Copy the flags register to the destination variable
      appendInst(
        Set(dstOp, RegOperand(Processor.REG_FL))
      )

    elif isinstance(inst, threeaddr.GreaterThanEqual):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      srcOpA, patchOff = _getOperand(localVars, patches, len(code), inst.srca)
      srcOpB, _ = _getOperand(localVars, patches, patchOff, inst.srcb)

      # Subtract the second variable from the first variable
      appendInst(
        Sub(srcOpA, srcOpB)
      )

      # Mask the less-than and zero flags in the flags register
      appendInst(
        And(
          RegOperand(Processor.REG_FL),
          ShortImmOperand(Processor.FLAG_LESS | Processor.FLAG_ZERO)
        )
      )

      # Copy the flags temporarily
      # XXX The flags register should probably be updated if it isn't the
      # destination operand of an instruction.
      appendInst(
        Set(RegOperand(Processor.REG_X0), RegOperand(Processor.REG_FL))
      )

      # Check whether the flags are zero
      appendInst(
        Or(RegOperand(Processor.REG_X0), ShortImmOperand(0))
      )

      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)

      # Copy the flags register to the destination variable
      appendInst(
        Set(dstOp, RegOperand(Processor.REG_FL))
      )

    elif isinstance(inst, threeaddr.Equal):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      srcOpA, _ = _getOperand(localVars, patches, len(code), inst.srca)

      # Copy the first variable into a temporary register
      appendInst(
        Set(RegOperand(Processor.REG_X0), srcOpA)
      )

      srcOpB, _ = _getOperand(localVars, patches, len(code), inst.srcb)

      # Subtract the second variable from the first variable
      appendInst(
        Sub(RegOperand(Processor.REG_X0), srcOpB)
      )

      # Mask the zero flag in the flags register
      appendInst(
        And(RegOperand(Processor.REG_FL), ShortImmOperand(Processor.FLAG_ZERO))
      )

      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)

      # Copy the flags register to the destination variable
      assert Processor.FLAG_ZERO == 1
      appendInst(
        Set(dstOp, RegOperand(Processor.REG_FL))
      )

    elif isinstance(inst, threeaddr.NotEqual):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      srcOpA, _ = _getOperand(localVars, patches, len(code), inst.srca)

      # Copy the first variable into a temporary register
      appendInst(
        Set(RegOperand(Processor.REG_X0), srcOpA)
      )

      srcOpB, _ = _getOperand(localVars, patches, len(code), inst.srcb)

      # Subtract the second variable from the first variable
      appendInst(
        Sub(RegOperand(Processor.REG_X0), srcOpB)
      )

      # Mask the zero flag in the flags register
      appendInst(
        And(RegOperand(Processor.REG_FL), ShortImmOperand(Processor.FLAG_ZERO))
      )

      # Negate the result
      appendInst(
        Xor(RegOperand(Processor.REG_FL), ShortImmOperand(Processor.FLAG_ZERO))
      )

      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)

      # Copy the flags register to the destination variable
      assert Processor.FLAG_ZERO == 1
      appendInst(
        Set(dstOp, RegOperand(Processor.REG_FL))
      )

    elif isinstance(inst, threeaddr.Neg):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      dstOp, patchOff = _getOperand(localVars, patches, len(code), inst.dst)
      srcOp, _ = _getOperand(localVars, patches, patchOff, inst.src)

      # Copy the source to the destination
      appendInst(
        Set(dstOp, srcOp)
      )

      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)

      # NOT the result (one's complement)
      appendInst(
        Xor(dstOp, ShortImmOperand(-1))
      )

      # Add one to the result (two's complement)
      appendInst(
        Add(dstOp, ShortImmOperand(1))
      )

    elif isinstance(inst, threeaddr.Not):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      dstOp, patchOff = _getOperand(localVars, patches, len(code), inst.dst)
      srcOp, _ = _getOperand(localVars, patches, patchOff, inst.src)

      # Copy the source to the destination
      appendInst(
        Set(dstOp, srcOp)
      )

      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)

      # Generate the operation
      appendInst(
        Xor(dstOp, ShortImmOperand(-1))
      )

    elif isinstance(inst, threeaddr.Mul):
      # This is separate from the other binary operations because it modifies
      # both of its operands.
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      srcOpA, _ = _getOperand(localVars, patches, len(code), inst.srca)

      # Load the first variable into X0
      appendInst(
        Set(RegOperand(Processor.REG_X0), srcOpA)
      )

      srcOpB, _ = _getOperand(localVars, patches, len(code), inst.srcb)

      # Loaf the second variable into X1
      appendInst(
        Set(RegOperand(Processor.REG_X1), srcOpB)
      )

      # Generate the operation
      appendInst(
        Mul(RegOperand(Processor.REG_X0), RegOperand(Processor.REG_X1))
      )

      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)

      # Copy X0 into the destination variable
      appendInst(
        Set(dstOp, RegOperand(Processor.REG_X0))
      )

    elif isinstance(inst, threeaddr.BinOp):
      localOff = _reserveLocal(localVars, localOff, inst.dst)

      srcOpA, _ = _getOperand(localVars, patches, len(code), inst.srca)

      # Load the first variable into X0
      appendInst(
        Set(RegOperand(Processor.REG_X0), srcOpA)
      )

      srcOpB, _ = _getOperand(localVars, patches, len(code), inst.srcb)

      if isinstance(inst, threeaddr.And):
        oper = And
      elif isinstance(inst, threeaddr.Xor):
        oper = Xor
      elif isinstance(inst, threeaddr.Or):
        oper = Or
      elif isinstance(inst, threeaddr.Div):
        oper = Div
      elif isinstance(inst, threeaddr.Add):
        oper = Add
      elif isinstance(inst, threeaddr.Sub):
        oper = Sub
      else:
        raise NotImplementedError(inst) # XXX

      # Generate the operation
      appendInst(
        oper(RegOperand(Processor.REG_X0), srcOpB)
      )

      dstOp, _ = _getOperand(localVars, patches, len(code), inst.dst)

      # Copy X0 into the destination variable
      appendInst(
        Set(dstOp, RegOperand(Processor.REG_X0))
      )

    elif isinstance(inst, threeaddr.Jump):
      targetOp, _ = _getOperand(localVars, patches, len(code), inst.target)

      # Jump to the given address
      appendInst(
        Set(RegOperand(Processor.REG_IP), targetOp)
      )

    elif isinstance(inst, threeaddr.IfZeroJump):
      srcOp, _ = _getOperand(localVars, patches, len(code), inst.src)

      # Set the flags register
      appendInst(
        Or(ShortImmOperand(0), srcOp)
      )

      # Check the flags register
      appendInst(
        If(RegOperand(Processor.REG_FL), ShortImmOperand(Processor.FLAG_ZERO))
      )

      targetOp, _ = _getOperand(localVars, patches, len(code), inst.target)

      # Jump to the given address
      appendInst(
        Set(RegOperand(Processor.REG_IP), targetOp)
      )

    elif isinstance(inst, threeaddr.IfNotZeroJump):
      srcOp, _ = _getOperand(localVars, patches, len(code), inst.src)

      # Set the flags register
      appendInst(
        Or(ShortImmOperand(0), srcOp)
      )

      # Invert the zero flag
      appendInst(
        Xor(RegOperand(Processor.REG_FL), ShortImmOperand(Processor.FLAG_ZERO))
      )

      # Check the flags register
      appendInst(
        If(RegOperand(Processor.REG_FL), ShortImmOperand(Processor.FLAG_ZERO))
      )

      targetOp, _ = _getOperand(localVars, patches, len(code), inst.target)

      # Jump to the given address
      appendInst(
        Set(RegOperand(Processor.REG_IP), targetOp)
      )

    else:
      raise NotImplementedError(inst) # XXX

  # Go through the list of patches and substitute in the correct label
  # addresses.
  for label, off in patches:
    assert code[off] == PATCH_WORD
    code[off] = labels[label]

  return (code, labels)
