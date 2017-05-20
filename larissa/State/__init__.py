
class State(object):

    def __init__(self, project):
        self.project = project
        
        # Init the state
        self.binary = self.project.loader.main_bin.map_sections(None)

        self._populate_plugins()

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

# Location of plugins
plugins_dir = os.path.dirname(plugins.__file__)
