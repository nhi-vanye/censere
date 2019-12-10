require(packrat)
packrat::restore()

args <- commandArgs(trailingOnly = TRUE)

rmarkdown::render('test-notebook.Rmd', 'pdf_document', params=list(database_path = args[1]) )


