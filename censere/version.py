# Adopt a standard versioning numbering conventions
# based on the date and python package standards
# https://www.python.org/dev/peps/pep-0440/#public-version-identifiers

# Release Phase : dev - Development; a - Alpha; b - Beta; rc - Release Candidate; '' (empty) - final
__release_phase__ = ''

# Build number within the release phase
# If building under CI then we overwrite this in setup.py
__release_phase_build__ = ''

import datetime

import pkg_resources

__version__ = "{}{}{}".format(datetime.date.today().strftime("%Y.%j"), __release_phase__, __release_phase_build__)
try:
    __version__ =  pkg_resources.get_distribution('censere').version
# pylint: disable-next=bare-except
except: # nosec try_except_pass
    pass
