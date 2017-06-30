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
