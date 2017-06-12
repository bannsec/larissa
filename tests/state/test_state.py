import os
import larissa
import pytest

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","bin")

def test_state_64_simple_pic_pie():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()

def test_state_64_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()

def test_state_32_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_nopie"))
    state = proj.factory.entry_state()

def test_state_32_simple_nopic_pie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_pie"))
    state = proj.factory.entry_state()

def test_state_32_simple_pic_pie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))
    state = proj.factory.entry_state()

def test_state_project_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))
    state = proj.factory.entry_state()

    # This should fail
    with pytest.raises(Exception):
        state.project = 123

def test_state_return_binary():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))
    state = proj.factory.entry_state()
    state.binary
