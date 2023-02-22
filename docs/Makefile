all:: documentation.pdf documentation.html

documentation.pdf: documentation.md assets
	pandoc --filter pandoc-crossref -o documentation.pdf documentation.md

documentation.html: documentation.md templates/default.html
	pandoc --filter pandoc-crossref --number-sections --standalone --template templates/default.html --toc -o documentation.html documentation.md
