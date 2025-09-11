# Prolyl Isomerisation Benchmark

This repository contains the data and scripts required to reproduce the results from my MSc thesis _On the Computational Modelling of Prolyl–Peptide_ cis–trans _Isomerisation: Benchmarking DFT Approaches with N–Acetylproline Methylamide_


## Repository Structure

```
.
├── Data/              # Raw and processed dataset files
├── Scripts/           # Analysis and processing scripts with configuration files
└── Images/            # Flow diagrams used in this REAME
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

![Flowchart depicting the data pipeline for the analysis of the prolyl conformational distribution](./Images/PDB_flowchart.png)

2. Preparation of starting geometry

![Flowchart depicting the data pipeline for the preparation of the starting geometry](./Images/Preparation_flowchart.png)

3. Relaxed surface scans

![Flowchart depicting the data pipeline for the solvated 2D relaxed surface scans](./Images/Solvent_scans_flowchart.png)

4. Identification of minimum energy geometries

![Flowchart depicting the data pipeline for the identification of minimum energy geometries](./Images/Geometry_Optimisation_flowchart.png)

6. Identification of transition state geometries

![Flowchart depicting the data pipeline for the identification of transition state geometries](./Images/TS_search_flowchart.png)

8. Benchmark of DFT functionals

![Flowchart depicting the data pipeline for the benchmark of DFT functionals](./Images/Benchmark_Flowchart.png)
