# -*- coding: utf-8 -*-
#
#  setup.py
#

from setuptools import setup

VERSION = '0.1.0'

setup(
    name='slowclap',
    description="Clap detection using your microphone and portaudio.",
    long_description=open('README.rst').read(),
    url="https://github.com/larsyencken/slowclap/",
    version=VERSION,
    author="Lars Yencken",
    author_email="lars@yencken.org",
    license="ISC",
    scripts=[],
    packages=['slowclap'],
    install_requires=[
        'PyAudio>=0.2.7',
        'numpy>=1.8.0',
    ],
    entry_points={
        'console_scripts': [
            'slowclap = slowclap:main',
        ],
    },
)
