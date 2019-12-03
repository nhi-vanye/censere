# Developers on Windows should run this script before pushing anything
# to gitlab.com
# 
# CI/CD has been enabled for the projects and will attempt to build
# the code as checked in. 
#
# This script automates the steps that occur as part of the CI build
# in an attempt to minimise failures that will occur otherwise

# On Linux the following steps are run as part of the Docker build
#
# * lint
# * pytest
# * package
#
# This script runs the same

# pylint is not currently in requirements.txt because its not needed to run the application (only to develop it) - and it takes a long time to install it in the docker container, so for now you will need to install pylint manually (once) in the virtual environment (you did create one didn't you ?)

write-host "Running pylint"
write-host "=============="

pylint censere
if ( !$? ) {

  write-host "pylint failed: You must fix before continuing"
  return

}

write-host "Running pytest"
write-host "=============="
pytest tests
if ( !$? ) {

  write-host "pytest failed: You must fix before continuing"
  return
}

write-host "Packaging"
write-host "========="
python setup.py bdist_wheel
if ( !$? ) {

  write-host "Failed to package censere project"
  return
}

write-host "To install run the following"
write-host ""
write-host "  pip install dist/censere*whl"

