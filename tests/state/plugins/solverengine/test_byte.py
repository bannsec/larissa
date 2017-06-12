import os
import larissa
import pytest

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","..","..","bin")

def test_solverengine_byte_basic():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state)

def test_solverengine_byte_addr_and_symbol():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,address=1234,symbolic=True)
    # Should have bailed before this
    assert not hasattr(b,"value")

def test_solverengine_byte_addr_and_value():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,address=1234,value=123)
    # Should have bailed before this
    assert not hasattr(b,"value")

def test_solverengine_byte_value_too_big():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,value=0x100)
    # Should have bailed before this
    assert not hasattr(b,"value")

def test_solverengine_byte_symbolic():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,symbolic=True)
    assert not b.concrete

def test_solverengine_byte_load_from_state():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,address=0x0040053c)
    assert b.value == 0x55

"""
# Taking this out for now until I get the Ast type definition thing worked out
def test_solverengine_byte_value_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,address=0x0040053c)
    b.value = "bad"
    # Basically, it should just ignore setting this
    assert b.value == 0x55
"""

def test_solverengine_byte_get_state():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,address=0x0040053c)
    b.state

def test_solverengine_byte_state_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,address=0x0040053c)
    with pytest.raises(Exception):
        b.state = "blerg"

def test_solverengine_byte_bad_address():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,address=0x0040053c)
    b.address = "test"
    assert b.address == 0x0040053c

def test_solverengine_byte_load_from_mem_bad_address():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state)
    b._load_from_memory()

def test_solverengine_byte_repr():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,address=0x0040053c)
    repr(b)

def test_solverengine_byte_str():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,address=0x0040053c)
    assert str(b) == "U"
    b = larissa.State.plugins.SolverEngine.Byte(state)
    assert str(b) == ""

def test_solverengine_byte_int():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Byte(state,address=0x0040053c)
    assert int(b) == 0x55
    b = larissa.State.plugins.SolverEngine.Byte(state)
    assert int(b) == -1
    b = larissa.State.plugins.SolverEngine.Byte(state,symbolic=True)
    assert type(int(b)) in [int, long]

def test_solverengine_byte_page_attr():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    # No page assigned to start
    assert state.memory[0x100].page.mapped == False

    # Assign page
    state.memory.pages[0] = larissa.State.plugins.memory.Page(7)
    assert state.memory[0x100].page.execute == True

    # Test byte that is not from memory
    b = state.se.Byte()
    assert b.page == None

