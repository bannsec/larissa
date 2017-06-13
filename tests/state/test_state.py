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

def test_state_symbol():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    main = state.symbol('main')
    assert str(state.memory[main.addr:main.addr+32]) == 'UH\x89\xe5H\x83\xec \x89}\xfcH\x89u\xf0H\x89U\xe8\xe8\xd0\xff\xff\xff\xb8\x00\x00\x00\x00\xc9\xc3f'
    fini = state.symbol('_fini')
    assert str(state.memory[fini.addr:fini.addr+32]) == 'H\x83\xec\x08H\x83\xc4\x08\xc3\x00\x00\x00\x01\x00\x02\x00Hello World!\x00\x00\x00\x00'
