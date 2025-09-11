#!/bin/bash

walltime="168:00:00"
n_cpu="8"
memory="256GB"

{
	IFS=";"
	while read geometry; do
		name=${geometry}_CCSD
		input=${geometry}.xyz
		mkdir ${name}
		export name=$name input=$input walltime=$walltime n_cpu=$n_cpu memory=$memory
		envsubst '$name,input' < CCSD.inp > $name/$name.inp
		envsubst '$name,$walltime,$n_cpu,$memory' < orca_template.pbs > $name/$name.pbs
		cp  *.xyz ./$name/
		cd $name/
		qsub $name.pbs
		cd ..
	done
} < geometries.config
