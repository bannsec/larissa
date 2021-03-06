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

def test_state_symbol():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    main = state.symbol('main')
    assert str(state.memory[main.addr:main.addr+32]) == 'UH\x89\xe5H\x83\xec \x89}\xfcH\x89u\xf0H\x89U\xe8\xe8\xd0\xff\xff\xff\xb8\x00\x00\x00\x00\xc9\xc3f'
    fini = state.symbol('_fini')
    assert str(state.memory[fini.addr:fini.addr+32]) == 'H\x83\xec\x08H\x83\xc4\x08\xc3\x00\x00\x00\x01\x00\x02\x00Hello World!\x00\x00\x00\x00'

    # Bug where the actual symbol was being updated...
    assert main.addr == state.symbol('main').addr

def test_state_reverse_symbol():
    for arch in ["amd64","ia32"]:
        for binary in ["simple_pic_pie","simple_nopic_nopie"]:
            print("Loading {0} {1}".format(arch, binary))
            proj = larissa.Project(os.path.join(bin_path,arch,binary))
            state = proj.factory.entry_state()
            main = state.symbol('main')
            resolved = state.symbol(main.addr)
            assert resolved.name == "main"
            assert resolved.addr == main.addr
            assert resolved.source == binary

            # Shared libary
            printf = state.symbol("printf")
            resolved = state.symbol(printf.addr)
            assert "printf" in resolved.name
            assert resolved.addr == printf.addr
            assert "libc" in resolved.source


def test_state_symbol_copy_exclude():
    proj = larissa.Project(os.path.join(bin_path,"ia32","reloc_copy_nopic_nopie"))
    state = proj.factory.entry_state()
    assert state.symbol('stdout').source == "reloc_copy_nopic_nopie"
    assert "libc" in state.symbol('stdout',exclude=['reloc_copy_nopic_nopie']).source
