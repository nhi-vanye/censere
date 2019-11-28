Developer Guidelines
====================

Build-All Scripts
=================

There are two helper scripts that all developers should use

Either `build-all.sh` (on macOS or Linux) or `build-all.ps` on Windows.

They automate the steps that are run as part of the CI build - on your local 
computer.

The scripts must be used before pushing up to GitLab or the CI builds will 
fail.

They are not identical, `build-all.sh` will run the build step in a Docker 
Container, `build-all.ps1` does not.



Preferred Conduct
-----------------

* I (richard) personally don't like PEP8. As I'm getting older I'm
finding it harder to separate the characters at a glance, therefore
I prefer addition spacing (horizontal and vertical) to aid fast
assimulation.
* Don't reformat other peoples code unless you are chnaging it for other reasons
* Use the following import order
* * standard libraries (i.e. sys, os, logging)
* * third party additional libraries required for the application
* * local modules
* Try not to use import wildcards.
