import os
import larissa
import pytest

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","..","..","bin")


def test_regs_ia32_names():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    # Just make sure we have some basics
    regs = ["eax","ebx","ecx","edx","esi","edi","ebp","esi","esp"]
    assert all( hasattr(state.regs,reg) and getattr(state.regs,reg).name == reg for reg in regs)

def test_regs_amd64_names():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    # Just make sure we have some basics
    regs = ["eax","ebx","ecx","edx","esi","edi","rax","rbx","rcx","rdx","rdi","rsi","rip","rbp","rsp"]
    assert all( hasattr(state.regs,reg) and getattr(state.regs,reg).name == reg for reg in regs)

def test_regs_amd64_sizes():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    assert state.regs.zf.size == 1
    assert state.regs.al.size == 8
    assert state.regs.al.bytes.length == 1
    assert state.regs.ax.size == 16
    assert state.regs.ax.bytes.length == 2
    assert state.regs.eax.size == 32
    assert state.regs.eax.bytes.length == 4
    assert state.regs.rax.size == 64
    assert state.regs.rax.bytes.length == 8
    assert state.regs.xmm0.size == 128
    assert state.regs.xmm0.bytes.length == 16
    assert state.regs.ymm0.size == 256
    assert state.regs.ymm0.bytes.length == 32

def test_reg_amd64_repr():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    assert "rax" in repr(state.regs.rax)

def test_reg_set_constant():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    assert int(state.regs.rax.bytes) == 0
    state.regs.rax.set(31337)
    assert int(state.regs.rax.bytes) == 31337

def test_reg_int_hex_str():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    state.regs.rbx.set(12345)
    assert int(state.regs.rbx) == 12345
    assert hex(state.regs.rbx).strip("L") == hex(12345)
    # Endianness stuff?
    assert str(state.regs.rbx) == '90\x00\x00\x00\x00\x00\x00'

def test_reg_int_zf():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()
    state.regs.zf.set(1)
    assert int(state.regs.zf) == 1

def test_reg_symbolic_to_concrete():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()

    eax = state.regs.eax._triton_symbolic_register
    assert not eax.isSymbolized()

    state.regs.eax.make_symbolic()
    eax = state.regs.eax._triton_symbolic_register
    assert eax.isSymbolized()
    
    state.regs.eax.set(1337)
    eax = state.regs.eax._triton_symbolic_register
    assert not eax.isSymbolized()
    assert int(state.regs.eax) == 1337

def test_reg_symbolic_bytes():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    state = proj.factory.entry_state()

    # Make a subset of eax symbolic
    state.regs.al.make_symbolic()
    eax = state.regs.eax.bytes

    assert set(state.se.any_n_int(eax,1000)) == set([x for x in range(0x100)])

    # Make sure we can get symbolic flag
    state.regs.zf.make_symbolic()
    zf = state.regs.zf.bytes

    # No constraints. This should be 0 or 1
    assert set(state.se.any_n_int(zf, 10)) == set((0,1))
