import os
import larissa
import pytest

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","..","..","bin")

def test_solverengine_solver_allbyte():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    b = state.se.Byte(symbolic=True)
    # Effectively, there are no constraints on this byte, should have all possibilities
    assert len(set(state.se.any_n_int(b,256))) == 256

def test_solverengine_solver_allbyte_str():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    b = state.se.Byte(symbolic=True)
    # Effectively, there are no constraints on this byte, should have all possibilities
    assert len(set(state.se.any_n_str(b,256))) == 256

def test_solverengine_solver_multibyte():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    b = state.se.Bytes(symbolic=True, length=2)
    # Effectively, there are no constraints on this byte, should have all possibilities
    assert len(set(state.se.any_n_int(b,512))) == 512

def test_solverengine_solver_repr():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    repr(state.se)

def test_solverengine_solver_anyint_badobj():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    assert state.se.any_int("bad") == None

def test_solverengine_solver_any_n_int_badobj():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    assert state.se.any_n_int("bad",5) == None

def test_solverengine_solver_any_n_int_from_int():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    assert state.se.any_n_int(1337,5) == [1337]

def test_solverengine_solver_anystr_badobj():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    assert state.se.any_str(None) == None

def test_solverengine_solver_anynstr_badobj():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    assert state.se.any_n_str(None,12) == None

def test_solverengine_solver_anystr_trivial():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    state = proj.factory.entry_state()
    assert state.se.any_str(77) == "M"
