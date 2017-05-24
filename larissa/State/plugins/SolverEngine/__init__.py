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
        whip_var = triton.ast.variable(whip)
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
                byte = triton.ast.bv(int(byte), size)
            else:
                # It's already an ast node.
                byte = byte.value

            #
            # Track extract statements
            #

            # The extract statement is kind 173
            if byte.getKind() == 173:
                childs = byte.getChilds()

                if len(childs) == 3:

                    # 233 is the root ast variable
                    if childs[2].getKind() == 233:
                        
                        # Make clear some assumptions for now
                        assert childs[0].getValue() - 7 == childs[1].getValue()
                        assert childs[1].getValue() % 8 == 0

                        # If this is the first time seeing it
                        if childs[2].getHash() not in vars_seen:
                            # Init the vector
                            vars_seen[childs[2].getHash()] = [childs[2]] + [False] * (childs[2].getBitvectorSize() / 8)

                        # Mark off that we've seen this slice
                        vars_seen[childs[2].getHash()][(childs[1].getValue()/8)+1] = True

            #
            # Make sure it's the right size
            #

            if byte.getBitvectorSize() != size:
                # Need to extend it
                byte = triton.ast.zx(size - byte.getBitvectorSize(), byte)

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

            # Loop through the mask
            for i, used in enumerate(vars[1:]):

                if not used:
                    # We haven't used this, don't let it take up solution space
                    ast = triton.ast.land( ast, triton.ast.extract((i*8)+7, i*8, vars[0]) == 0)

        
        return [option[whip_id].getValue() for option in triton.getModels(triton.ast.assert_(ast),n)]

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
            #if len(val) % 2 != 0:
            #    val = "0" + val

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
            self._whip[bits] = triton.newSymbolicVariable(bits)

        return self._whip[bits]

    def __repr__(self):
        return "<SolverEngine>"

    ##############
    # Properties #
    ##############

from .Byte import Byte
from .Bytes import Bytes
import triton
from binascii import unhexlify

import logging
logger = logging.getLogger("larissa.State.plugins.SolverEngine")
