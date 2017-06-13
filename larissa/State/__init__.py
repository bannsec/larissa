
class State(object):

    def __init__(self, project):
        self.project = project
        self._populate_plugins()

    def symbol(self, name):
        """Lookup symbol by name, return with address adjusted for loaded base."""
        symbol = copy(self.project.loader.main_bin.symbols[name])

        if symbol == None:
            return symbol

        # If it's relocatable, need to update the address
        if symbol.source in self.project.loader.shared_objects or self.project.loader.main_bin.address == 0:
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
