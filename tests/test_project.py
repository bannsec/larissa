import os
import larissa

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

