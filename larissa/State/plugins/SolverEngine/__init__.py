from .. import PluginBase

class SolverEngine(PluginBase):

    def __init__(self, state, *args, **kwargs):

        self.state = state

        # For now, need a whipping boy variable
        self._whip = {}

    def Byte(self, *args, **kwargs):
        """Instantiate a Byte object for the current state."""
        return Byte(self.state, *args, **kwargs)

    def Bytes(self, *args, **kwargs):
        """Instantiate a Bytes object for the current state."""
        return Bytes(self.state, *args, **kwargs)

    def any_int(self, obj):
        """Return a single possible int of this object."""
        if type(obj) not in [int, long, Byte, Bytes]:
            logger.error("Invalid type for obj of {0}".format(type(obj)))
            return

        ints = self.any_n_int(obj,1)

        # Couldn't find any
        if ints == []:
            return None

        return ints[0]

    def any_n_int(self, obj, n):
        """Return n possibilities."""
        if type(obj) not in [int, long, Byte, Bytes]:
            logger.error("Invalid type for obj of {0}".format(type(obj)))
            return

        # Silly
        if type(obj) in [int, long]:
            return [obj]

        # If the object is concrete, use it's own int method
        if obj.concrete:
            return [int(obj)]

        # If it's only one, just put it into a list
        if type(obj) is Byte:
            obj = [obj]

        # Correct for architecture endianness
        if self.state.project.loader.main_bin.endianness != 'little':
            bytes = reversed(obj)
        else:
            bytes = obj

        # Length in bits of this pseudo var
        size = len(bytes) * 8

        # Create a whip
        whip = self._get_whip(size)
        whip_var = self.state.ctx.getAstContext().variable(whip)
        whip_id = whip.getId()
        
        ast = None

        # Due to how Triton works, we need to track what slics of variables we have not used in this ast.
        vars_seen = {}

        # Generate an expression to evaluate
        for i, byte in enumerate(bytes):

            #
            # Make sure it's an ast
            # 

            # If it's concrete, just make it a bv
            if byte.concrete:
                byte = self.state.ctx.getAstContext().bv(int(byte), size)
            else:
                # It's already an ast node.
                byte = byte.value

            #
            # Track extract statements
            #

            if byte.getKind() == triton.AST_NODE.EXTRACT:
                childs = byte.getChilds()

                if len(childs) == 3:

                    if childs[2].getKind() == triton.AST_NODE.VARIABLE:
                        
                        # Make clear some assumptions for now
                        assert childs[0].getValue() - 7 == childs[1].getValue()
                        assert childs[1].getValue() % 8 == 0

                        # If this is the first time seeing it
                        if childs[2].getHash() not in vars_seen:
                            # Init the vector
                            # This amounts to a dictionary of lists, indexed by the unique hash id of the variable (i.e.: symvar_0)
                            # The list is meant to keep track of what bits we've seen in all these expressions, so we can ignore the bits that aren't used
                            # There is likely a better way to do this... This whole thing is because Triton gives extract expressions back. If we're not careful, we can get extra results for things we don't care about (bits that aren't involved in this expression)
                            # Structure: [astNode, bool slice1, bool slice2, ... bool slice n]
                            #vars_seen[childs[2].getHash()] = [childs[2]] + [False] * (childs[2].getBitvectorSize() / 8)

                            # Changing this to a bitmask instead to account for flags and other bit level adjustments
                            vars_seen[childs[2].getHash()] = [childs[2], 2**(childs[2].getBitvectorSize())-1]

                        # Mark off that we've seen this slice
                        #vars_seen[childs[2].getHash()][(childs[1].getValue()/8)+1] = True

                        # Mask off the bitmask of what we're using
                        #high = childs[0].getValue()
                        #low = childs[1].getValue()

                        # This is a hackish way to create a bitmask between two numbers...
                        """
                        mask = 0
                        i = low
                        while mask <= (2**high-1):
                            mask |= 1 << i
                            i += 1
                        """
                        mask = childs[2].getBitvectorMask()

                        vars_seen[childs[2].getHash()][1] &= ~mask

            #
            # Make sure it's the right size
            #

            if byte.getBitvectorSize() != size:
                # Need to extend it
                byte = self.state.ctx.getAstContext().zx(size - byte.getBitvectorSize(), byte)

            #
            # If this is the first one
            # 

            if ast is None:
                ast = byte

            else:
                # Add this ast on to what we already have
                ast = ast + (byte << (i*8))

        # Setup our whip to be equal
        ast = ast == whip_var

        # Loop through the vars we've seen and zero out any parts we're not using
        for vars in vars_seen.values():

            # New approach using bitmask....
            this_ast = vars[0]
            mask = vars[1]

            # If there's bits unused, tell the solver to ignore them
            if mask != 0:
                ast = self.state.ctx.getAstContext().land( ast, this_ast & mask == 0)

            """
            # Loop through the mask
            for i, used in enumerate(vars[1:]):

                if not used:
                    # We haven't used this, don't let it take up solution space
                    ast = self.state.ctx.getAstContext().land( ast, self.state.ctx.getAstContext().extract((i*8)+7, i*8, vars[0]) == 0)
            """

        
        return [option[whip_id].getValue() for option in self.state.ctx.getModels(ast,n)]

    def any_n_str(self, obj, n):
        """Return a list of n possible strings for this object."""
        if type(obj) not in [int, long, Byte, Bytes]:
            logger.error("Invalid type for obj of {0}".format(type(obj)))
            return

        # Silly
        if type(obj) in [int, long]:
            return [chr(obj)]

        # Utilize any_n_int to get the values
        ints = self.any_n_int(obj, n)

        strs = []
        fmt = "{:0" + str(len(obj)*2) + "x}"

        # Convert
        for val in ints:

            val = fmt.format(val)
            # int -> hex
            #val = hex(val)[2:].strip("L")

            # make sure hex is padded right
            if len(val) % 2 != 0:
                val = "0" + val

            # hex to str
            val = unhexlify(val)

            # Adjust for endianness
            if self.state.project.loader.main_bin.endianness == 'little':
                val = val[::-1]

            strs.append(val)

        return strs

    def any_str(self, obj):
        """Return one possible string."""
        if type(obj) not in [int, long, Byte, Bytes]:
            logger.error("Invalid type for obj of {0}".format(type(obj)))
            return

        strs = self.any_n_str(obj,1)

        # Couldn't find any
        if strs == []:
            return None

        return strs[0]

    def _get_whip(self, bits):
        """Return a whip variable of bits size."""

        # Create it if we need to
        if bits not in self._whip:
            self._whip[bits] = self.state.ctx.newSymbolicVariable(bits)

        return self._whip[bits]

    def __repr__(self):
        return "<SolverEngine>"

    ##############
    # Properties #
    ##############

from .Byte import Byte
from .Bytes import Bytes
from binascii import unhexlify
import triton

import logging
logger = logging.getLogger("larissa.State.plugins.SolverEngine")
