
class Factory(object):

    def __init__(self, project):
        """Take in the project file."""

        self.project = project

    def entry_state(self):
        # Start a new state
        state = State(self.project)
        
        # Init the state
        state.binary = self.project.loader.main_bin.map_sections(state)

        # Return it
        return state


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

from larissa.Project import Project
from larissa.State import State
