#!/bin/bash

config=$1
walltime="2:00:00"
n_cpu="16"
memory="8GB"
{	
	IFS=";"
	while read name input x y solvent; do
		echo ${name}
		mkdir ${name}
		export name=$name input=$input x=$x y=$y solvent=$solvent walltime=$walltime n_cpu=$n_cpu memory=$memory
		envsubst '$name,$input,$x,$y,$z,$solvent' < xtb_2d_scan.inp > $name/$name.inp
		envsubst '$name,$walltime,$n_cpu,$memory < orca_template.pbs > $name/$name.pbs
		cp ${input} ./$name/
		cd $name/
		qsub $name.pbs
		cd ..
	done
} < "$config"
