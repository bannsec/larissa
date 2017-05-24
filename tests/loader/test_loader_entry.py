import os
import larissa

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","bin")

def test_entry_64_simple_pic_pie():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    assert proj.loader.main_bin.entry == 0x620

def test_entry_64_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    assert proj.loader.main_bin.entry == 0x400430

def test_entry_32_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_nopie"))
    assert proj.loader.main_bin.entry == 0x8048310

def test_entry_32_simple_nopic_pie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_pie"))
    assert proj.loader.main_bin.entry == 0x490

def test_entry_32_simple_pic_pie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))
    assert proj.loader.main_bin.entry == 0x480

