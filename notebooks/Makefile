

SIM=/dev/null

all::

html::
	quarto render --to html -P dbpathname:data/${SIM}.db

pdf::
	quarto render --to pdf -P dbpathname:data/${SIM}.db

preview::
	quarto preview -P dbpathname:data/${SIM}.db

clean::
	rm -f  *.html.md *.pdf.md
	rm -rf _output/ *_files/ site_libs/
