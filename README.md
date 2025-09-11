# Prolyl Isomerisation Benchmark

This repository contains the data and scripts required to reproduce the results from my MSc thesis _On the Computational Modelling of Prolyl–Peptide_ cis–trans _Isomerisation: Benchmarking DFT Approaches with N–Acetylproline Methylamide_


## Repository Structure

```
.
├── data/              # Raw and processed dataset files
├── scripts/           # Analysis and processing scripts with configuration files
└── images/            # Flow diagrams used in this REAME
```

## Requirements

To reproduce this analysis, you will need:

- Python 3.x
- Required Python packages:
  - Numpy 1.24.x
- R 4.3.x
- Required R packages:
  -  tidyverse
  -  hrbrthemes
  -  cetcolor
  -  jsonlite
  -  legendry
  -  ggtext
  -  ggsci
  -  ggh4x
- ORCA 6.0 (with xtb)

## Usage

1. Analysis of the conformational distribution of prolyl residues in the PDB

2. Preparation of starting geometry

3. Relaxed surface scans

4. Identification of minimum energy geometries

5. Identification of transition state geometries

6. Benchmark of DFT functionals


