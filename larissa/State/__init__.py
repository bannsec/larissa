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
            for base in sorted(self.posix.base_addrs):
                if self.posix.base_addrs[base] < address:
                    logger.debug("Found base for address {0} at {1}".format(address, base))
                    break
            else:
                logger.error("Unable to find base for address {0}".format(address))
                return

            # Library
            for shared_object in self.project.loader.shared_objects.values():
                if os.path.basename(shared_object.filename) != base:
                    continue

                out = [shared_object.symbols[sym] for sym in shared_object.symbols if shared_object.symbols[sym].addr == address - self.posix.base_addrs[base]]

                if out == []:
                    return None
                out = copy(out[0])
                out.addr += self.posix.base_addrs[base]
                return out

            # Main bin PIE
            if self.project.loader.main_bin.address == 0:
                out = [self.project.loader.main_bin.symbols[sym] for sym in self.project.loader.main_bin.symbols if self.project.loader.main_bin.symbols[sym].addr == address - self.posix.base_addrs[base]]
                if out == []:
                    return None
                out = copy(out[0])
                out.addr += self.posix.base_addrs[base]
                return out

            # Main bin non-PIE
            else:
                out = [self.project.loader.main_bin.symbols[sym] for sym in self.project.loader.main_bin.symbols if self.project.loader.main_bin.symbols[sym].addr == address]
                if out == []:
                    return None
                return copy(out[0])

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

# Location of plugins
plugins_dir = os.path.dirname(plugins.__file__)
