#! /usr/bin/env python3

import os
import datetime

from setuptools import setup

# loads __release_phase__ etc from version.py
exec( open( 'censere/version.py').read() )

if 'CI_COMMIT_SHA' in os.environ:

    __release_phase_build__ = '1+'

    if 'CI_COMMIT_REF_NAME' in os.environ:

        __release_phase_build__ = os.environ['CI_COMMIT_REF_NAME'] + '-'

    __release_phase_build__ = __release_phase_build__ + os.environ['CI_COMMIT_SHA']
    

version = "{}{}{}".format(datetime.date.today().strftime("%Y.%j"), __release_phase__, __release_phase_build__)

setup( name='censere',
    version=version,
    description='Mars Population Simulation software',
    author='Mars Censere Team',
    url='https://gitlab.com/mars-society-uk/science/mars-censere/mars-censere',
    license='GPLv2',
    packages=[
        'censere',
        'censere.actions',
        'censere.config',
        'censere.db',
        'censere.events',
        'censere.models',
        'censere.utils'
    ],
)

