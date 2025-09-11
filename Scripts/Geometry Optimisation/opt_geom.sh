#!/bin/bash

config=$1
walltime="2:00:00"
n_cpu="16"
memory="8GB"

echo $config

cat < $config
{	
	IFS=";"
	while read name input; do
		echo ${name}
		mkdir ${name}
		export name=$name input=$input walltime=$walltime n_cpu=$n_cpu memory=$memory
		envsubst '$name,$input' < opt_geom.inp > $name/$name.inp
		envsubst '$name,$walltime,$n_cpu,$memory' < orca_template.pbs > $name/$name.pbs
		cp ${input} ./$name/
		cd $name/
		qsub $name.pbs
		cd ..
	done
} < "$config"
