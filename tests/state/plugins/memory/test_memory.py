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

def test_memory_page_mapped():
    p = larissa.State.plugins.memory.Page(1)
    assert p.mapped == False

    p = larissa.State.plugins.memory.Page(1,mapped=True)
    assert p.mapped == True

    p.mapped = False
    assert p.mapped == False

    # Invalid, should just be ignored
    p.mapped = None
    assert p.mapped == False

def test_memory_page_read_setter():
    p = larissa.State.plugins.memory.Page(0)
    assert p.read == False
    p.read = True
    assert p.read == True
    p.read = False
    assert p.read == False
    p.read = None
    assert p.read == False

def test_memory_page_write_setter():
    p = larissa.State.plugins.memory.Page(0)
    assert p.write == False
    p.write = True
    assert p.write == True
    p.write = False
    assert p.write == False
    p.write = None
    assert p.write == False

def test_memory_page_execute_setter():
    p = larissa.State.plugins.memory.Page(0)
    assert p.execute == False
    p.execute = True
    assert p.execute == True
    p.execute = False
    assert p.execute == False
    p.execute = None
    assert p.execute == False
