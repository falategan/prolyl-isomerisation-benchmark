#!/bin/bash

config=$1
walltime="168:00:00"
n_cpu="16"
memory="8GB"

{	
	IFS=";"
	while read name input x y z; do
		echo ${name}
		mkdir ${name}
		export name=$name input=$input x=$x y=$y z=$z walltime=$walltime
		envsubst '$name,$input,$x,$y,$z' < xtb_3d_scan.inp > $name/$name.inp
		envsubst '$name,$walltime,$n_cpu,$memory' < orca_template.pbs > $name/$name.pbs
		cp ${input} ./$name/
		cd $name/
		qsub $name.pbs
		cd ..
	done
} < "$config"
