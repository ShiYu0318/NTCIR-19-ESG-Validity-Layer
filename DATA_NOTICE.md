# Data and prediction artifact notice

This repository intentionally does **not** redistribute source paragraph text,
the AI CUP competition JSON files, ML-Promise source JSON files, source PDFs,
or reconstructed Korean page text.

The released `*.csv.gz` files are row-level research artifacts. They contain a
row identifier, source-report URL, fold rotation, gold labels, predicted
labels, and legal-state identifiers; they contain no paragraph text. The
text-free AI CUP corpus index adds company/ticker metadata and SHA-256 hashes
of paragraph text so the published corpus audit and duplicate check can be
recomputed without revealing the paragraphs.

The MIT License applies only to the software in this repository. It does not
replace or expand the terms governing AI CUP, ML-Promise, source sustainability
reports, or artifacts derived from those sources. Users are responsible for
obtaining source datasets through their official distribution channels and
complying with the applicable terms. ML-Promise was released under
CC BY-NC-SA 4.0; the original paper and dataset distribution should be cited
when its derived prediction records are used.

This notice records provenance and scope; it is not legal advice.
