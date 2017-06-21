import os
import larissa
import pytest

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","..","..","bin")

def test_solverengine_bytes_basic():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Bytes(state)

def test_solverengine_bytes_addr_and_symbolic():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Bytes(state,address=1234,symbolic=True)
    assert not hasattr(b,"length")

def test_solverengine_bytes_symbolic():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Bytes(state,length=32,symbolic=True)
    # Should be 32 bytes in length
    assert len(b) == 32
    # Every byte should be symbolic
    assert all((not x.concrete for x in b))

def test_solverengine_bytes_address():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Bytes(state,length=8,address=0x0040053c)
    expected = [0x55,0x48,0x89,0xe5,0x48,0x83,0xec,0x20]
    for x,y in zip(b,expected):
        assert x.value == y

def test_solverengine_bytes_repr():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Bytes(state,length=8,address=0x0040053c)
    assert "address" in repr(b)
    assert "length" in repr(b)
    assert "Symbolic" not in repr(b)

    b = larissa.State.plugins.SolverEngine.Bytes(state,length=8,symbolic=True)
    assert "address" not in repr(b)
    assert "length" in repr(b)
    assert "Symbolic" in repr(b)

def test_solverengine_bytes_getitem():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Bytes(state,length=8,address=0x0040053c)
    assert int(b[2]) == 0x89

def test_solverengine_bytes_str():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Bytes(state,length=5,address=0x0040053c)
    assert str(b) == "UH\x89\xe5H"

def test_solverengine_bytes_bytes_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Bytes(state,length=5,address=0x0040053c)
    # If this fails, it should simply not set
    orig = b.bytes
    b.bytes = "test"
    assert b.bytes == orig

def test_solverengine_bytes_length_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Bytes(state,length=5,address=0x0040053c)
    # If this fails, it should simply not set
    l = b.length
    b.length = "test"
    assert b.length == l

def test_solverengine_bytes_address_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Bytes(state,length=5,address=0x0040053c)
    # If this fails, it should simply not set
    orig = b.address
    b.address = "blerg"
    assert b.address == orig

def test_solverengine_bytes_state_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = larissa.State.plugins.SolverEngine.Bytes(state,length=5,address=0x0040053c)

    with pytest.raises(Exception):
        b.state = "blerg"

def test_solverengine_bytes_initial_value():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = state.se.Bytes(length=16,value=0x12345678)
    assert int(b) == 0x12345678

def test_solverengine_bytes_initial_value_and_address():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = state.se.Bytes(length=16,value=0x12345678,address=0x1234)
    assert not hasattr(b,"length")

def test_solverengine_bytes_invalid_value():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = state.se.Bytes(length=16,value=12.5)
    assert int(b) == 0

def test_solverengine_bytes_invalid_value_too_big():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = state.se.Bytes(length=4,value=0xffffffffff)
    assert int(b) == 0

def test_solverengine_bytes_overload_hex():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = state.se.Bytes(length=16,value=0x123456)
    assert hex(b) == "0x123456"

def test_solverengine_bytes_zero_string():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = state.se.Bytes(length=16,value=0)
    assert str(b) == "\x00"*16

def test_solverengine_bytes_long_addr():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    b = state.memory[0x0040053cL: 0x0040053cL + 5]
    assert str(b) == "UH\x89\xe5H"
