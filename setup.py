# -*- coding: utf-8 -*-
 
from setuptools import setup, find_packages
 
import IReadiTunes

setup(
    name='IReadiTunes',
    version=IReadiTunes.__version__,
    packages=find_packages(),
    author="Mickael Gerber",
    author_email="mickaelgerberdev@gmail.com",
	description="Tool to get any information about iTunes tracks and playlists quickly and easily",
	long_description_content_type = "text/markdown",
	long_description=open('README.md').read(),
    url='https://github.com/mickael2054/IReadiTunes.git',
	install_requires=[],
    classifiers=[
        "Programming Language :: Python",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
    ],
    license="MIT", 
)