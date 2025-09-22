# Prolyl Isomerisation Benchmark

This repository contains the data and scripts required to reproduce the results from my MSc thesis _On the Computational Modelling of Prolyl–Peptide_ cis–trans _Isomerisation: Benchmarking DFT Approaches with N–Acetylproline Methylamide_

## Repository Structure

```
.
├── Data/              # Raw and processed dataset files
├── Images/            # Flow diagrams used in this README
└── Scripts/           # Analysis and processing scripts with configuration files
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

### 1. Analysis of the conformational distribution of prolyl residues in the PDB

![Flowchart depicting the data pipeline for the analysis of the prolyl conformational distribution](./Images/PDB_flowchart.png)

#### 1.1 Prepare proline geometries

1. Select your set of proteins and download their `.pdb` crystallographic coordinates to a dedicated directory. 
2. Write their PDB ids of the proteins into a newline ("\\n") separated text file (`pisces_pdb_ids.txt`). The files must be named `{ID}.pdb`, where {ID} is its PDB id.
3. Read the atomic coordinates of the proline residues with `get_prolines.pbs`. `read_proline.awk` must be in the same directory as `get_prolines.pbs`. Set the path to the PDB directory in the script before executing:
```
qsub get_prolines.pbs
```
4. Use the `assemble_prolines.rmd` R notebook to pivot `proline_atoms.csv` to a wide format.

#### 1.2 Add adjacent groups

1. Read the atoms from adjacent residues by executing `get_acetyl.pbs`, `get_amide.pbs` and `get_methyl.pbs`. `read_acetyl.awk` must be in the same directory as `get_acetyl.pbs`, `read_amide.awk` must be in the same directory as `get_amide.pbs`, and `read_methyl.awk` must be in the same directory as `get_methyl.pbs`. Each directory must also contain the wide-format proline coordinates (`proline_residues.csv`) . Set the path to the PDB directory in each script before executing:
```
qsub get_acetyl.pbs
qsub get_amide.pbs
qsub get_methyl.pbs
```
2. Combine atoms from adjacent residues with the wide-format residue records with the `assemble_AcProNMe.rmd` R notebook. This requires the files for the atomic coordinates of the proline residues (`proline_residues.csv`), and the adjacent groups (`acetyl_atoms.csv`, `amide_atoms.csv` and `methyl_atoms.csv`).

#### 1.3 Convert Cartesian atomic coordinates to internal coordinates

Execute `csv2internal.py` to generate internal coordinates for each residue. `csv2internal.py` imports modules from `xyz2internal.py` - ensure this script is included in the environment or working directory. `csv2internal.py` takes three arguments: the path to the Cartesian coordinates (`AcProNMe.csv`), the path to the configuration file defining the internal coordinates (`AcProNMe_internal.config`), and the path for the output (`PDB.intl`)

```
python csv2internal.py ./AcProNMe.csv ./AcProNMe_internal.config ./PDB.intl
```

#### 1.4 Filter and generate figures of the conformational distribution

Use `analyse_pdb.rmd` to analyse the distribution of conformations within the PDB sample (`PDB.intl`).

### 2. Preparation of starting geometry

![Flowchart depicting the data pipeline for the preparation of the starting geometry](./Images/Preparation_flowchart.png)

3. Relaxed surface scans

![Flowchart depicting the data pipeline for the solvated 2D relaxed surface scans](./Images/Solvent_scans_flowchart.png)

4. Identification of minimum energy geometries

![Flowchart depicting the data pipeline for the identification of minimum energy geometries](./Images/Geometry_Optimisation_flowchart.png)

6. Identification of transition state geometries

![Flowchart depicting the data pipeline for the identification of transition state geometries](./Images/TS_search_flowchart.png)

8. Benchmark of DFT functionals

![Flowchart depicting the data pipeline for the benchmark of DFT functionals](./Images/Benchmark_Flowchart.png)
