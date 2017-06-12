import os
import larissa
import pytest

# Where are we
here = os.path.dirname(os.path.realpath(__file__))

def test_project_load_64_simple_pic_pie():
    proj = larissa.Project(os.path.join(here,"bin","amd64","simple_pic_pie"))

def test_project_load_64_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(here,"bin","amd64","simple_nopic_nopie"))

def test_project_load_32_simple_nopic_nopie():
    proj = larissa.Project(os.path.join(here,"bin","ia32","simple_nopic_nopie"))

def test_project_load_32_simple_nopic_pie():
    proj = larissa.Project(os.path.join(here,"bin","ia32","simple_nopic_pie"))

def test_project_load_32_simple_pic_pie():
    proj = larissa.Project(os.path.join(here,"bin","ia32","simple_pic_pie"))

def test_project_repr():
    proj = larissa.Project(os.path.join(here,"bin","ia32","simple_pic_pie"))
    repr(proj)

def test_project_loader_badsetter():
    proj = larissa.Project(os.path.join(here,"bin","ia32","simple_pic_pie"))
    
    with pytest.raises(Exception):
        proj.loader = 123

def test_project_get_factory():
    proj = larissa.Project(os.path.join(here,"bin","ia32","simple_pic_pie"))
    proj.factory
    
def test_project_factory_badsetter():
    proj = larissa.Project(os.path.join(here,"bin","ia32","simple_pic_pie"))
    
    with pytest.raises(Exception):
        proj.factory = 123
        
def test_project_filename_badsetter():
    proj = larissa.Project(os.path.join(here,"bin","ia32","simple_pic_pie"))
    
    with pytest.raises(Exception):
        proj.filename = 123

    with pytest.raises(Exception):
        proj.filename = "............"
