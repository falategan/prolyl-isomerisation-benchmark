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

### Analysis of the conformational distribution of prolyl residues in the PDB

![Flowchart depicting the data pipeline for the analysis of the prolyl conformational distribution](./Images/PDB_flowchart.png)

#### 1. Prepare proline geometries

1. Select your set of proteins and download their `.pdb` crystallographic coordinates to a dedicated directory. 
2. Write their PDB ids of the proteins into a newline ("\\n") separated text file ([pisces_pdb_ids.txt](<./Data/PDB Conformations/pisces_pdb_ids.txt>)). The files must be named `{ID}.pdb`, where {ID} is its PDB id.
3. Read the atomic coordinates of the proline residues with [get_prolines.pbs](Scripts/PDB/get_prolines.pbs). [read_proline.awk](Scripts/PDB/read_proline.awk) must be in the same directory as [get_prolines.pbs](Scripts/PDB/get_prolines.pbs). Set the path to the PDB directory in the script before executing:
```shell
qsub get_prolines.pbs
```
4. Use the [assemble_prolines.rmd](Scripts/PDB/assemble_prolines.rmd) R notebook to pivot `proline_atoms.csv` to a wide format.

#### 2. Add adjacent groups

1. Read the atoms from adjacent residues by executing [get_acetyl.pbs](Scripts/PDB/get_acetyl.pbs), [get_amide.pbs](Scripts/PDB/get_amide.pbs) and [get_methyl.pbs](Scripts/PDB/get_methyl.pbs). [read_acetyl.awk](Scripts/PDB/read_acetyl.awk), [read_amide.awk](Scripts/PDB/read_amide.awk),and [read_methyl.awk](Scripts/PDB/read_methyl.awk) must be in the same directory as their respective pbs scripts. Each directory must also contain the wide-format proline coordinates (`proline_residues.csv`) . Set the path to the PDB directory in each script before executing:
```shell
qsub get_acetyl.pbs
qsub get_amide.pbs
qsub get_methyl.pbs
```
2. Combine atoms from adjacent residues with the wide-format residue records with the [assemble_AcProNMe.rmd](Scripts/PDB/assemble_AcProNMe.rmd) R notebook. This requires the files for the atomic coordinates of the proline residues (`proline_residues.csv`), and the adjacent groups (`acetyl_atoms.csv`, `amide_atoms.csv` and `methyl_atoms.csv`).

#### 3. Convert Cartesian atomic coordinates to internal coordinates

Execute [csv2internal.py](<Scripts/Internal Coordinates/csv2internal.py>) to generate internal coordinates for each residue. [csv2internal.py](<Scripts/Internal Coordinates/csv2internal.py>) imports modules from [xyz2internal.py](<Scripts/Internal Coordinates/xyz2internal.py>). Ensure this script is included in the environment or working directory. [csv2internal.py](<Scripts/Internal Coordinates/csv2internal.py>)  takes three arguments: 
1) the path to the Cartesian coordinates (`AcProNMe.csv`)
2) the path to the configuration file defining the internal coordinates ([csv2internal.py](<Scripts/Internal Coordinates/AcProNMe_internal.config>))
3) the path for the output (`PDB.intl`)

```shell
python csv2internal.py ./AcProNMe.csv ./AcProNMe_internal.config ./PDB.intl
```

#### 4. Filter and generate figures of the conformational distribution

Use [analyse_pdb.rmd](Scripts/PDB/analyse_pdb.rmd) to analyse the distribution of conformations within the PDB sample (`PDB.intl`).

### ORCA Computational Chemistry Overview

This repository provides shell scripts for preparation and execution of various ORCA computations (geometry optimisation, 2D relaxed surface scans, 3D relaxed surface scans, transition state searches, DFT single point energies, and CCSD(T) single point energies with CBS extrapolation). 

This scheme simplifies the execution of a large number of ORCA jobs in parallel using the following files:
- **{task}.inp**: These are template ORCA input files specifying the parameters for a basic ORCA run
- **{task}.config**: These semicolon-delimited files list the job names, input file paths, and job-specific parameters. Each line provides specifications for a new ORCA run.
- **orca_template.pbs**: This is a template PBS jobscript from which the jobscripts for all the ORCA jobs are generated. The resulting jobscript specifies the resource assignment for the PBS scheduler, generates a temporary working directory in the (manually) specified location, and initiates the ORCA run.
- **{task.sh}**: This bash shell script generates output directories, populates the `{task}.inp` and `orca_template.pbs` templates, and submits the jobscript to the PBS job queue for each line in `{task}.config`.

### Preparation of the starting geometry

![Flowchart depicting the data pipeline for the preparation of the starting geometry](./Images/Preparation_flowchart.png)

Optimise the geometry of the AcProNHMe crystallographic structure [AcProNHMe_Crystal.xyz](<Data/Structure Preparation/AcProNHMe_Crystal.xyz>) at the r<sup>2</sup>SCAN-3c level of theory by executing [opt_geom.sh](<Data/Geometry Optimisation/opt_geom.sh>). The script requires a configuration file ([geom_prep.config](<Data/Structure Preparation/geom_prep.config>)) listing the job name and the path to the atomic coordinates separated by a semicolon. Ensure the ORCA geometry optimisation input file ([opt_geom.inp](<Data/Geometry Optimisation/opt_geom.inp>)) and the template jobscript ([orca_template.pbs](Scripts/orca_template.pbs)) are included in the working directory or PATH variables.

```shell
./opt_geom.sh  geom_prep.config
```

### Solvated relaxed surface scans

![Flowchart depicting the data pipeline for the solvated 2D relaxed surface scans](./Images/Solvent_scans_flowchart.png)

This section makes use of the initial optimised geometry generate in the [Preparation of the starting geometry Section](#preparation-of-the-starting-geometry).

#### 1. Execute relaxed surface scans 

Run the [xtb_2D_scan.sh](<Scripts/Relaxed Surface Scans/xtb_2D_scan.sh>) script, starting at the optimised starting geometry ([AcProNHMe_opt.xyz](<Data/Structure Preparation/AcProNHMe_opt.xyz>).

```shell
./xtb_2D_scan.sh solvent_scans.config
```

The semicolon-delimited configuration file ([solvent_scans.config](<Scripts/Relaxed Surface Scans/solvent_scans.config>)) has the following columns:
```csvs
Job Name; Path to Starting Geometry; First Scan Coordinate; Second Scan Coordinate; Solvent
```

The scan coordinates specify the scanning dimension, starting coordinate, end coordinate and number of steps for each scanning dimension in the ORCA `%geom SCAN` format.

#### 2. Convert the Cartesian atomic coordinates to internal coordinates

Use [xyz2internal.py](<Scripts/Internal Coordinates/xyz2internal.py>) to generate internal coordinates for each scan. The script takes three arguments: 
1) the path to the atomic coordinates (`xtb_H2O_scan.allxyz` / `xtb_CHCl3_scan.allxyz` / `xtb_DMF_scan.allxyz` / `xtb_gas_scan.allxyz`),
2) the path to the internal coordinate configuration file ([AcProNHMe_internal.config](<Scripts/Internal Coordinates/AcProNHMe_internal.config>)
3) the output path (`xtb_H2O_scan.intl`/`xtb_CHCl3_scan.intl`/`xtb_DMF_scan.intl`/`xtb_gas_scan.intl`).

```shell
python xyz2internal.py xtb_{solvent}_scan.allxyz AcProNHMe_internal.config xtb_{solvent}_scan.intl
```

#### 3. Analyse the surface scans 

Use the [Analyse_solvent_scans.rmd](<Scripts/Relaxed Surface Scans/Analyse_solvent_scans.rmd>) R notebook to plot the results and identify local minima. The notebook requires the internal coordinates for all the surface scans (`xtb_{solvent}_scan.intl`), and the single point energies of each geometry (`xtb_{solvent}_scan.relaxscanact.dat`)



### Explore gas-phase reaction paths

This section makes use of the initial optimised geometry generate in the [Preparation of the starting geometry Section](#preparation-of-the-starting-geometry).

####  Identification of minimum energy geometries

![Flowchart depicting the data pipeline for the identification of minimum energy geometries](./Images/Geometry_Optimisation_flowchart.png)

##### 1. _Trans_ relaxed surface scans

Execute [xtb_3d_scans.sh](<Scripts/Relaxed Surface Scans/xtb_3d_scans.sh>) to scan the _trans_ conformational landscape starting with the initial optimised geometry ([AcProNHMe_opt.xyz](<Data/Structure Preparation/AcProNHMe_opt.xyz>)).


```shell
./xtb_3d_scans.sh minima_scans.config
```

The configuration file ([minima_scans.config](<Scripts/Relaxed Surface Scans/minima_scans.config>) has the following columns:
```csvs
Job Name; Path to Starting Geometry; First Scanning Coordinate; Second Scanning Coordinate; Third Scanning Coordinate
```

##### 2. Convert the Cartesian atomic coordinates to internal coordinates

```shell
python xyz2internal.py minima_fwd_scan.allxyz AcProNHMe_internal.config minima_fwd_scan.intl
python xyz2internal.py minima_rev_scan.allxyz AcProNHMe_internal.config minima_rev_scan.intl
```

##### 3. Identify local minima

Use the [minima_scans.rmd](<Scripts/Relaxed Surface Scans/minima_scans.rmd>) R notebook to plot the results and identify local minima. The notebook requires the internal coordinates for all the surface scans ([minima_fwd_scan.intl](<Data/Minimum Geometries/minima_fwd_scan.intl>) / [minima_rev_scan.intl](<Data/Minimum Geometries/minima_rev_scan.intl>)), and the single point energies of each geometry ([minima_fwd_scan.relaxscanact.dat](<Data/Minimum Geometries/minima_fwd_scan.relaxscanact.dat>) / [minima_rev_scan.relaxscanact.dat](<Data/Minimum Geometries/minima_rev_scan.relaxscanact.dat>))

##### 4. Optimise local minima

Optimise the geometry of the approximate local minima ([minima_fwd_scan.940.xyz](<Data/Minimum Geometries/minima_fwd_scan.940.xyz>) / [minima_fwd_scan.1524.xyz](<Data/Minimum Geometries/minima_fwd_scan.1524.xyz>) / [minima_fwd_scan.44007.xyz](<Data/Minimum Geometries/minima_fwd_scan.44007.xyz>) / [minima_fwd_scan.44678.xyz](<Data/Minimum Geometries/minima_fwd_scan.44678.xyz>)) at the r<sup>2</sup>SCAN-3c level op theory by executing [opt_geom.sh](<Scripts/Geometry Optimisation/opt_geom.sh>).

```shell
./opt_geom.sh opt_minima.config
```

##### 5. Convert the Cartesian atomic coordinates to internal coordinates

Generate internal coordinates for the optimised local minima.

```shell
python xyz2internal.py transG_g-endo.xyz AcProNHMe_internal.config transG_g-endo.intl
python xyz2internal.py transG_g-exo.xyz AcProNHMe_internal.config transG_g-exo.intl
python xyz2internal.py cisD_g-exo.xyz AcProNHMe_internal.config cisD_g-exo.intl
python xyz2internal.py cisA_g-endo.xyz AcProNHMe_internal.config cisA_g-endo.intl
```

##### 6. Characterise local minima

Use the [Analyse_minima.rmd](<Scripts/Geometry Optimisation/Analyse_minima.rmd>) R notebook to calculate puckering coordinates and tabulate the properties of the local minimum geometries. This notebook requires the internal coordinates of all optimised minima ([transG_g-endo.intl](<Data/Minimum Geometries/transG_g-endo.intl>) / [transG_g-exo.intl](<Data/Minimum Geometries/transG_g-endo.intl>) / [cisD_g-exo.intl](<Data/Minimum Geometries/transG_g-endo.intl>) / [cisA_g-endo.intl](<Data/Minimum Geometries/transG_g-endo.intl>) ) and their ORCA property files ([minima_fwd_scan.940.property.json](<Data/Minimum Geometriesminima_fwd_scan.940.property.json>) / [minima_fwd_scan.1534.property.json](<Data/Minimum Geometries/minima_fwd_scan.1534.property.json>) / [minima_fwd_scan.44007.property.json](<Data/Minimum Geometries/minima_fwd_scan.44007.property.json>) / [minima_fwd_scan.44678.property.json](<Data/Minimum Geometries/minima_fwd_scan.44678.property.json>)).

#### Identification of gas-phase transition state geometries

![Flowchart depicting the data pipeline for the identification of transition state geometries](./Images/TS_search_flowchart.png)

##### 1. Isomerisation path relaxed surface scans

Execute `xtb_3d_scans.sh` to scan the conformational landscape between the _cis_ and _trans_ isomeric states, starting with the initial optimised geometry (`AcProNHMe_opt.xyz`). 

```shell
./xtb_3d_scans.sh TS_scans.config
```

##### 2. Convert the Cartesian atomic coordinates to internal coordinates

```shell
python xyz2internal.py TS_ff_scan.allxyz AcProNHMe_internal.config TS_ff_scan.intl
python xyz2internal.py TS_fr_scan.allxyz AcProNHMe_internal.config TS_fr_scan.intl
python xyz2internal.py TS_rf_scan.allxyz AcProNHMe_internal.config TS_rf_scan.intl
python xyz2internal.py TS_rr_scan.allxyz AcProNHMe_internal.config TS_rr_scan.intl
```

##### 3. Identify candidate transition states

Use the `Analyse_TS_scans.rmd` R notebook to plot the results and identify saddle points. The notebook requires the internal coordinates for all the surface scans (`TS_ff_scan.intl`/`TS_fr_scan.intl`/`TS_rf_scan.intl`/`TS_rr_scan.intl`), and the single point energies of each geometry (`TS_ff_scan.relaxscanact.dat`/`TS_fr_scan.relaxscanact.dat`/`TS_rf_scan.relaxscanact.dat`/`TS_rr_scan.relaxscanact.dat`).

##### 4. Optimise candidate transition states

```shell
./TS_search.sh TS_search.config
```
The shell script ([TS_search.sh](<Scripts/Transition State Searches/TS_search.sh>)) requires the transition state search input file ([TS_search.inp](<Scripts/Transition State Searches/TS_search.inp>)) and the ORCA job template ([orca_template.pbs](Scripts/orca_template.pbs)) in the working directory or PATH variables. The configuration file ([TS_search.config](<Scripts/Transition State Searches/TS_search.config>)) has the following columns:

```csvs
Job Name; Path to Input Geometry
```
##### 5. High-resolution surface scans near unsuccessful candidates

Perform two-dimensional relaxed surface scans around the candidates that failed to produce first-order saddle points ([TS_fr_scan.18441.xyz](<Data/Transition States/TS_fr_scan.18441.xyz>)/[TS_rf_scan.10748.xyz](<Data/Transition States/TS_rf_scan.10748.xyz>)). 

```
./xtb_2d_scan.sh TS_scans_hi-res.config
```
[xtb_2d_scan.sh](<Scripts/Relaxed Surface Scans/xtb_2d_scan.sh>) requires the two-dimensional surface scan input file ([xtb_2d_scan.inp](<Scripts/Transition State Searches/xtb_2d_scan.inp>)) and the ORCA job template ([orca_template.pbs](Scripts/orca_template.pbs)) in the working directory or PATH variables. The configuration file ([TS_scans_hi-res.config](<Scripts/Transition State Searches/TS_scans_hi-res.config>)) has the following columns:

```csvs
Job Name; Path to Starting Geometry; First Scan Coordinate; Second Scan Coordinate; Solvent
```

##### 6. Convert the Cartesian atomic coordinates to internal coordinates

```shell
python xyz2internal.py fr_18441_hi-res_scan.allxyz AcProNHMe_internal.config fr_18441_hi-res_scan.intl
python xyz2internal.py rf_10748_hi-res_scan.allxyz AcProNHMe_internal.config rf_10748_hi-res_scan.intl
```

##### 7. Identify new candidate transition states

The R notebook, [Inspect_hi-res_scans.rmd](<Scripts/Relaxed Surface Scans/Inspect_hi-res_scans.rmd>), produces plots from which new candidate saddle points may be selected. The notebook requires the internal coordinates for the refined surface scans ([fr_18441_hi-res_scan.intl](<Data/Transition States/fr_18441_hi-res_scan.intl>) / [rf_10748_hi-res_scan.intl](<Data/Transition States/rf_10748_hi-res_scan.intl>)), and the single point energies of each geometry ([fr_18441_hi-res_scan.relaxscanact.dat](<Data/Transition States/fr_18441_hi-res_scan.relaxscanact.dat>) / [rf_10748_hi-res_scan.relaxscanact.dat](<Data/Transition States/rf_10748_hi-res_scan.relaxscanact.dat>)).

##### 8. Optimise new candidate transition states

```shell
./TS_search_hi-res.sh TS_search_hi-res.config
```
The shell script ([TS_search.sh](<Scripts/Transition State Searches/TS_search.sh>)) requires the transition state search input file ([TS_search_hi-res.inp](<Scripts/Transition State Searches/TS_search_hi-res.inp>)) and the ORCA job template ([orca_template.pbs](Scripts/orca_template.pbs)) in the working directory or PATH variables.

This transition state search requires three optimised geometries along the reaction path: 
1) a geometry that precedes the transition state on the reaction path ([rf_10748_hi-res_scan.263.xyz](<Data/Transition States/rf_10748_hi-res_scan.263.xyz>) / [fr_18441_hi-res_scan.268.xyz](<Data/Transition States/fr_18441_hi-res_scan.268.xyz>))
2) a geometry near the expected transition state ([rf_10748_hi-res_scan.284.xyz](<Data/Transition States/rf_10748_hi-res_scan.284.xyz>) / [fr_18441_hi-res_scan.288.xyz](<Data/Transition States/fr_18441_hi-res_scan.288.xyz>))
3) a geometry the follows the transition state on the path ([rf_10748_hi-res_scan.305.xyz](<Data/Transition States/rf_10748_hi-res_scan.305.xyz>) / [fr_18441_hi-res_scan.308.xyz](<Data/Transition States/fr_18441_hi-res_scan.308.xyz>))

The configuration file ([TS_search_hi-res.config](<Scripts/Transition State Searches/TS_search_hi-res.config>)) has the following columns:

```csvs
Job Name; Path to geometry 1; Path to Geometry 2; Path to Geometry 3
```

##### 9. Convert the Cartesian atomic coordinates to internal coordinates

Generate internal coordinates for the first-order saddle points ([anti-endo.xyz](<Data/Transition States/anti-endo.xyz>)/[syn-endo.xyz](<Data/Transition States/syn-endo.xyz>)/[anti-exo.xyz](<Data/Transition States/anti-exo.xyz>)/[syn-exo.xyz](<Data/Transition States/syn-exo.xyz>)) identified by both the primary and refined transition state searches.

```shell
python xyz2internal.py anti-endo.xyz AcProNHMe_internal.config anti-endo.intl
python xyz2internal.py syn-endo.xyz AcProNHMe_internal.config syn-endo.intl
python xyz2internal.py anti-exo.xyz AcProNHMe_internal.config anti-exo.intl
python xyz2internal.py syn-exo.xyz AcProNHMe_internal.config syn-exo.intl
```

##### 10. Characterise transition states

Use the R notebook [Analyse_Transition_States.rmd](<Scripts/Transition State Searches/Analyse_Transition_States.Rmd>) to calculate puckering coordinates and tabulate the properties of the transition state geometries. This notebook requires the internal coordinates of all optimised transition states ([anti-endo.intl](<Data/Transition States/anti-endo.intl>) / [syn-endo.intl](<Data/Transition States/syn-endo.intl>) / [anti-exo.xyz](<Data/Transition States/anti-exo.intl>) / [syn-exo.intl](<Data/Transition States/syn-exo.intl>)) and their ORCA property files ([anti-endo.property.json](<Data/Transition States/anti-endo.property.json>) / [syn-endo.property.json](<Data/Transition States/syn-endo.property.json>) / [anti-exo.property.json](<Data/Transition States/anti-exo.property.json>) / [syn-exo.property.json](<Data/Transition States/syn-exo.property.json>)).


### Benchmark of DFT functionals

![Flowchart depicting the data pipeline for the benchmark of DFT functionals](./Images/Benchmark_Flowchart.png)

This section uses the minimum energy geometries derived in the [Identification of minimum energy geometries section](#identification-of-minimum-energy-geometries) and the transition state geometries derived in the [Identification of minimum energy geometries section](#identification-of-minimum-energy-geometries) and the transition states derived in the [Identification of gas-phase transition state geometries section](#identification-of-gas-phase-transition-state-geometries).

#### Calculate CCSD(T)/CBS single point energies

```shell
./CCSD.sh geometries.config
```

The configuration file ([geometries.config](<Scripts/Single Point Energies/geometries.config>)) has a single column providing the names of the critical point geometries (`transG_g-endo` / `transG_g-exo` / `cisD_g-exo` / `cisA_g-endo` / `anti-endo` / `anti-exo` / `syn-endo` / `syn-exo`)

The shell script ([CCSD.sh](<Scripts/Single Point Energies/CCSD.sh>)) requires the CCSD(T)/CSB input file ([CCSD.inp](<Scripts/Single Point Energies/CCSD.inp>)), the ORCA job template ([orca_template.pbs](Scripts/orca_template.pbs)) and the critical point geometries ([transG_g-endo.xyz](<Data/Minimum Geometries/transG_g-endo.xyz>) / [transG_g-exo.xyz](<Data/Minimum Geometries/transG_g-exo.xyz>) / [cisD_g-exo.xyz](<Data/Minimum Geometries/cisD_g-exo.xyz>) / [cisA_g-endo.xyz](<Data/Minimum Geometries/cisA_g-endo.xyz>) / [anti-endo.xyz](<Data/Transition States/anti-endo.xyz>) / [syn-endo.xyz](<Data/Transition States/syn-endo.xyz>) / [anti-exo.xyz](<Data/Transition States/anti-exo.xyz>) / [syn-exo.xyz](<Data/Transition States/syn-exo.xyz>)) in the working directory or PATH variables. 

#### Calculate DFT single point energies

```shell
./DFT_energies.sh
```

The shell script ([DFT_energies.sh](<Scripts/Single Point Energies/DFT_energies.sh>)) requires the DFT single point energy input file ([DFT_energies.inp](<Scripts/Single Point Energies/DFT_energies.inp>)), the ORCA job template ([orca_template.pbs](Scripts/orca_template.pbs)) and the critical point geometries ([transG_g-endo.xyz](<Data/Minimum Geometries/transG_g-endo.xyz>) / [transG_g-exo.xyz](<Data/Minimum Geometries/transG_g-exo.xyz>) / [cisD_g-exo.xyz](<Data/Minimum Geometries/cisD_g-exo.xyz>) / [cisA_g-endo.xyz](<Data/Minimum Geometries/cisA_g-endo.xyz>) / [anti-endo.xyz](<Data/Transition States/anti-endo.xyz>) / [syn-endo.xyz](<Data/Transition States/syn-endo.xyz>) / [anti-exo.xyz](<Data/Transition States/anti-exo.xyz>) / [syn-exo.xyz](<Data/Transition States/syn-exo.xyz>)), the geometry configuration file ([geometries.config](<Scripts/Single Point Energies/geometries.config>)) and the level-of-theory configuration file ([DFT_LoT.config](<Scripts/Single Point Energies/DFT_LoT.config>)) in the working directory or PATH variables. 

The geometry configuration file ([geometries.config](<Scripts/Single Point Energies/geometries.config>)) has a single column providing the names of the critical point geometries (`transG_g-endo` / `transG_g-exo` / `cisD_g-exo` / `cisA_g-endo` / `anti-endo` / `anti-exo` / `syn-endo` / `syn-exo`)

The level-of-theory configuration file ([geometries.config](<Scripts/Single Point Energies/DFT_LoT.config.config>)) has the following columns:
```csvs
METHOD; BASIS SET
```

#### Analyse the accuracy of each DFT functional

Use the R notebook [Analyse_Benchmark.rmd](<Scripts/Single Point Energies/Analyse_Benchmark.Rmd>) to analyse the CCSD(T) CBS extrapolation, benchmark each DFT functional against the CCSD(T) reference and compare the effect of dispersion corrections. The notebook requires the property files from the CCSD(T)/CBS and DFT single point energy calculations.

## License
[GNU General Public License v3.0
](./LICENSE)
