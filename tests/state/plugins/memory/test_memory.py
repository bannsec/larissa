import os
import larissa
import pytest
import larissa.State.plugins.memory

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","..","..","bin")


def test_memory_get_byte():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    assert int(state.memory[0x0040053c]) == 0x55

def test_memory_get_bytes():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    assert str(state.memory[0x0040053c:0x400541]) == "UH\x89\xe5H"

def test_memory_getitem_baditemtype():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    assert state.memory["test"] == None

def test_memory_getitem_nonestart():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    assert state.memory[:12] == None

def test_memory_getitem_nonestop():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    assert state.memory[12:] == None

def test_memory_getitem_usingstep():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    assert state.memory[1:100:5] == None

def test_memory_setitem():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    state.memory[0] = str(state.memory[0x0040053c:0x400541])
    assert str(state.memory[0:5]) == str(state.memory[0x0040053c:0x400541])

def test_memory_store_unicode():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    state.memory[0] = u"Hello"
    assert str(state.memory[0:5]) == "Hello"

def test_memory_store_unhandled_type():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    state.memory[0x0040053c] = None
    assert int(state.memory[0x0040053c]) == 0x55

def test_memory_setitem_unhandled_key_type():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    state.memory[None] = None

def test_memory_get_pages():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    # TODO: For now, pages are not implemented
    assert state.memory.pages == {}

def test_memory_page_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    state.memory.pages = None
    assert state.memory.pages == {}

def test_memory_page_badsetter():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    state.memory.pages = None
    assert state.memory.pages == {}

def test_memory_page_permissions():
    p = larissa.State.plugins.memory.Page(1)
    assert p.read == True
    assert p.write == False
    assert p.execute == False

    p = larissa.State.plugins.memory.Page(2)
    assert p.read == False
    assert p.write == True
    assert p.execute == False

    p = larissa.State.plugins.memory.Page(4)
    assert p.read == False
    assert p.write == False
    assert p.execute == True

def test_memory_page_bad_prottype():
    p = larissa.State.plugins.memory.Page("test")
    with pytest.raises(Exception):
        p.prot

def test_memory_page_bad_prot_value():
    p = larissa.State.plugins.memory.Page(12)
    with pytest.raises(Exception):
        p.prot

"""
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
"""
