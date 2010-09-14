from setuptools import setup, find_packages

setup(
    name = "django-test-extensions",
    version = "0.8",
    author = "Gareth Rushgrove",
    author_email = "gareth@morethanseven.net",
    url = "http://github.com/garethr/django-test-extensions/",
    
    packages = find_packages('src'),
    package_dir = {'':'src'},
    license = "MIT License",
    keywords = "django testing",
    description = "A few classes to make testing django applications easier",
    install_requires=[
        'setuptools',
        'BeautifulSoup',
        'coverage',
    ],
    classifiers = [
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ]
)
