from setuptools import setup, find_packages

setup(
    name = "text_extensions",
    version = "0.1",
    
    packages = find_packages('src'),
    package_dir = {'':'src'},
)