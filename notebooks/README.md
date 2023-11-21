Notebooks
=========

This directory contains a set of data analysis notebooks.


These are developed using quarto, a formatting system for reproducible
research.

Quarto does support Python, but I've used R for the analysis.


Why R ?
=======

Implmenting the simulation and analysis in two different languages
means that there is no possibilty of sharing code and that means a
bug in the simulation cannot be masked by the same bug in analysis.

We also get the benefits of:

* The `ggplot2` library is a phenominally powerful charting library
and produces pleasing presentation quality charts out of the box
* Not having to work around the `pandas` DateTime limit limit of April 2262 (64 nanoseconds)
* I can still use SQL to query the database - I've done this rather
than use `tidyr` or `pandas` specifics so that its easier to build
alternate analysis tools just by looking at the SQL.
* Jupyter is powerful, but it really doesn't work well in a
git/distributed environment where we want tp use the same logic
over a wide range of input data sets.


I've skipped the really powerful RStudio IDE (much better than Jupyer
IMHO) and stayed with basic R cli to make it easy to reproduce.


