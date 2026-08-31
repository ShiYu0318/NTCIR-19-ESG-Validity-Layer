# NTCIR19 - ESG Validity Layer

## Abstract

ESG promise verification requires jointly predicted fields to satisfy hard
parent--child constraints, particularly when outputs are intended for
audit-oriented use. We study hierarchical projection as a retraining-free
validity layer for field-wise classifiers. Seven decision rules are compared
on identical cross-fitted probabilities and test rows in Chinese, followed by
projection-versus-argmax replication across English, French, Japanese, and
Korean corpora. Projection reduces the Chinese invalid-tuple rate from 12.55%
to zero by construction. Its official weighted macro-F1 contrast is undetected
($\Delta=-0.001$, $p_{\mathrm{Holm}}=1.000$), while pre-specified tuple accuracy
improves by $+0.035$ ($p_{\mathrm{Holm}}=.001$). Across 32 external
backbone-by-loss arms, tuple accuracy improves in all 32, whereas weighted
macro-F1 improves in 14. These results position hierarchical projection not as
a guaranteed route to higher field-wise scores, but as a practical way to
guarantee coherent outputs and repeatedly improve complete-output correctness,
with field-score trade-offs varying across models and corpora. Validity alone
does not settle which structured rule to use: searching all 17 legal states
instead of projecting greedily costs $-0.006$ tuple accuracy
($p_{\mathrm{Holm}}=.028$), an adverse pre-specified result we report in full.
Code and reproducibility artifacts are available in this repository.

## Quick start

Python 3.10 or newer is required. The analysis is offline and needs no GPU or
model download.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python reproduce.py
```

The full command performs the frozen 10,000-resample report-cluster bootstrap
and normally takes several minutes on a laptop CPU. It writes regenerated
artifacts under `outputs/`, then byte-compares all manuscript-facing table and
caption files against `reference/`. Success ends with:

```json
{"figure_source_verified": true, "status": "ok", "tables_verified": 8}
```

For a fast integrity check without recomputing statistics, run:

```bash
python reproduce.py --verify-inputs
```

Use `--output-dir PATH` to place generated files elsewhere. If `latexmk` is
available, Figure 1 is also compiled as a vector PDF; its generated definitions
and TikZ source are verified on every machine even when TeX is absent.

## Repository layout

All immutable reproduction inputs live under `inputs/`, grouped by corpus.
Each corpus owns its split manifests and run predictions; the AI CUP corpus
also carries the text-free corpus index used for the published audit.

```text
inputs/<corpus>/splits/
inputs/<corpus>/runs/<arm>/predictions/
inputs/aicup_zh/corpus_index.json.gz
```

`analysis/` regenerates the results, `paper/` contains the shared schema and
artifact readers, and `reference/` contains the manuscript-facing files used
for byte comparison.

## What is reproduced

The command regenerates manuscript Tables 1, 2, 3, 4, 6, 7, 8, and 9:

- the AI CUP corpus/hierarchy audit;
- the seven Chinese decision rules and pre-specified paired contrasts;
- same-document versus document-disjoint evaluation;
- legality cost across seven Chinese model/training arms;
- the five-corpus projection mechanism and invalid-tuple anatomy; and
- all 32 external backbone-by-loss arms behind the `32/32` tuple-accuracy and
  `14/32` weighted-F1 direction counts.

The curated input set contains exactly 300 gzip-compressed prediction files:
42 Chinese-anchor files, 54 files for the six additional Chinese arms, 192
M0/M1 files for the 32 external arms, and 12 M4 files for the four preselected
external backbones. Ten split manifests and one text-free AI CUP corpus index
provide grouping and audit metadata. 
## Deliberate exclusions

This capsule contains no paragraph text, competition source JSON, ML-Promise
source JSON, model weights, probability tensors, training checkpoints, or GPU
training code. The text-free corpus index contains identifiers, report URLs,
company/ticker metadata, labels, and paragraph hashes solely to reproduce the
published audit and grouping. See [DATA_NOTICE.md](DATA_NOTICE.md) before
redistributing the row-level artifacts.

## Licence and citation

The reproduction code is released under the [MIT License](LICENSE). That code
licence does not grant rights in source datasets or prediction records derived
from them. Citation metadata is provided in [CITATION.cff](CITATION.cff).
