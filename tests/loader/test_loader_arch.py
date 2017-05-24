import os
import larissa

# Where are we
here = os.path.dirname(os.path.realpath(__file__))
bin_path = os.path.join(here,"..","bin")

def test_project_load_64_simple_pic_pie():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_pic_pie"))
    assert proj.loader.main_bin.arch == 'x64'

def test_project_load_64_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(bin_path,"amd64","simple_nopic_nopie"))
    assert proj.loader.main_bin.arch == 'x64'

def test_project_load_32_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_nopie"))
    assert proj.loader.main_bin.arch == 'x86'

def test_project_load_32_simple_nopic_pie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_nopic_pie"))
    assert proj.loader.main_bin.arch == 'x86'

def test_project_load_32_simple_pic_pie():
    proj = larissa.Project(os.path.join(bin_path,"ia32","simple_pic_pie"))
    assert proj.loader.main_bin.arch == 'x86'

