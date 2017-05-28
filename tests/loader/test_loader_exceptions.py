import os
import larissa
import pytest

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","bin")

def test_loader_triton_bad_arch(monkeypatch):
    def get_arch():
        return "badarch"

    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))

    # Patch our elf file to return something invalid
    monkeypatch.setattr(proj.loader.main_bin.elffile, "get_machine_arch", get_arch)
    
    # This should fail
    with pytest.raises(Exception):
        proj.loader._set_triton_arch()

def test_loader_triton_bad_bits(monkeypatch):
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))

    # Patch our elf file to return something invalid
    monkeypatch.setattr(proj.loader.main_bin.elffile, "elfclass", 1337)
    
    # This should fail
    with pytest.raises(Exception):
        proj.loader._set_triton_arch()

def test_loader_load_all_bins_no_main_bin(monkeypatch):
    def load_bin(x):
        return None

    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))

    # Patch our elf file to return something invalid
    monkeypatch.setattr(proj.loader, "_load_bin", load_bin)
    
    # This should fail with error but no exception
    proj.loader._load_all_bins()

def test_loader_load_all_bins_no_shared_object_path(monkeypatch):
    class mock(object):
        pass

    def load_bin(x):
        m = mock()
        m.shared_objects = {'test':None}
        return m

    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))

    # Patch our elf file to return something invalid
    monkeypatch.setattr(proj.loader, "_load_bin", load_bin)
    
    # This should fail with an error message but no exception
    proj.loader._load_all_bins()

def test_loader_bad_file_attr():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))

    # It expects actual file object
    with pytest.raises(Exception):
        proj.loader.file = "blerg"

def test_loader_bad_project_attr():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))

    # Expects project object
    with pytest.raises(Exception):
        proj.loader.project = "blerg"

def test_loader_repr():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    
    repr(proj.loader)
