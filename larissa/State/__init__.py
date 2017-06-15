import logging
logger = logging.getLogger("larissa.State")

class State(object):

    def __init__(self, project):
        self.project = project
        self._populate_plugins()

    def symbol(self, name):
        """Lookup symbol by name, return with address adjusted for loaded base.
        If given integer instead of string, attempt reverse lookup of what symbol is at that address."""

        def symbol_by_address(self, address):
            """Given an address, attempt to reverse look-up a symbol at that location."""
            
            # Find the base module
            for name, base in sorted(self.posix.base_addrs.items(), key=operator.itemgetter(1),reverse=True):
                if base < address:
                    logger.debug("Found base for address {0} at {1} - {2}".format(address, base,name))
                    break
            else:
                logger.error("Unable to find base for address {0}".format(address))
                return

            obj = self.project.loader._lookup_obj_by_name(name)

            # PIE
            if obj.address == 0:
                out = [obj.symbols[sym] for sym in obj.symbols if obj.symbols[sym].addr == address - base]
            else:
                out = [obj.symbols[sym] for sym in obj.symbols if obj.symbols[sym].addr == address]

            # Didn't find it
            if out == []:
                return None

            out = copy(out[0])

            # Adjust for PIE base
            if obj.address == 0:
                out.addr += base

            return out


        # Reverse lookup
        if type(name) in [int, long]:
            return symbol_by_address(self, name)

        # Normal lookup
        symbol = copy(self.project.loader.symbol(name))

        if symbol == None:
            return symbol

        # If it's relocatable, need to update the address
        if self.project.loader._lookup_obj_by_name(symbol.source).address == 0:
            symbol.addr += self.posix.base_addrs[symbol.source]

        return symbol

        
    def _populate_plugins(self):
        """Dynamically find plugins, import and track them. Only call once."""
        
        # Keep track of what we loaded
        self.plugins = []

        # Grab list of plugins
        plugins = [plugin[:-3] for plugin in os.listdir(plugins_dir) if plugin.endswith(".py") and plugin != "__init__.py"]

        # Load up each plugin
        for plugin in plugins:

            # Dynamically load the module
            module = importlib.import_module("larissa.State.plugins.{0}".format(plugin))

            # Instantiate and save the class
            plugin_object = getattr(module,plugin.capitalize())(self)
            setattr(self, plugin, plugin_object)

            # Store that we loaded this
            self.plugins.append(plugin_object)


    ##############
    # Properties #
    ##############

    @property
    def project(self):
        return self.__project

    @project.setter
    def project(self, project):
        if type(project) is not Project:
            raise Exception("Invalid project of type {0}".format(type(project)))

        self.__project = project

    @property
    def binary(self):
        """The triton binary object for this state."""
        return self.__binary

    @binary.setter
    def binary(self, binary):
        self.__binary = binary

import os
import triton
from larissa.Project import Project
from . import plugins
import importlib
from copy import copy
import operator

# Location of plugins
plugins_dir = os.path.dirname(plugins.__file__)
