from setuptools import setup, find_packages

from bluesky import __version__

test_requirements = []
with open('requirements-test.txt') as f:
    test_requirements = [r for r in f.read().splitlines()]

setup(
    name='bluesky',
    version=__version__,
    license='GPLv3+',
    author='Joel Dubowy',
    author_email='jdubowy@gmail.com',
    packages=find_packages(),
    scripts=[
        'bin/bsp',
        'bin/bsp-csv2json'
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.5",
        "Operating System :: POSIX",
        "Operating System :: MacOS"
    ],
    package_data={
        # TODO: not sure how to specify package data for nested package.
        #   a)  {'hysplit': ['bdyfiles/*.']}
        #   b)  {'bluesky': ['hysplit/bdyfiles/*.']}
        #   c)  {'bluesky': {'hysplit': ['bdyfiles/*.']} }
        #   d)  some other way?
        # Update: the following way seems to be the only way to work both
        # via `python setup.py install` as well as via pip
        'bluesky': [
            'dispersers/hysplit/bdyfiles/*',
            'dispersers/vsmoke/images/*',
            'ecoregion/data/*'
        ]
    },
    url='https://github.com/pnwairfire/bluesky',
    description='BlueSky Framework rearchitected as a pipeable collection of standalone modules.',
    install_requires=[
        "pyairfire==2.*",
        "afconfig==1.*",
        "afdatetime>=1.0.2,<2.0.0",
        "afscripting==1.*",
        "afweb==1.*",
        "eflookup==1.*",
        "emitcalc==1.*",
        "fccsmap==1.*",
        "timeprofile==1.*",
        "met>=1.1.0,<2.0.0",
        "plumerise==1.*",
        "blueskykml==1.*",
        "apps-consume4==4.1.*"
    ],
    dependency_links=[
        "https://pypi.smoke.airfire.org/simple/pyairfire/",
        "https://pypi.smoke.airfire.org/simple/afconfig/",
        "https://pypi.smoke.airfire.org/simple/afdatetime/",
        "https://pypi.smoke.airfire.org/simple/afscripting/",
        "https://pypi.smoke.airfire.org/simple/eflookup/",
        "https://pypi.smoke.airfire.org/simple/emitcalc/",
        "https://pypi.smoke.airfire.org/simple/fccsmap/",
        "https://pypi.smoke.airfire.org/simple/timeprofile/",
        "https://pypi.smoke.airfire.org/simple/met/",
        "https://pypi.smoke.airfire.org/simple/plumerise/",
        "https://pypi.smoke.airfire.org/simple/blueskykml/",
        "https://pypi.smoke.airfire.org/simple/apps-consume4/"
    ],
    tests_require=test_requirements
)
