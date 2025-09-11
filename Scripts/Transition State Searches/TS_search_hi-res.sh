#!/bin/bash

config=$1
walltime="24:00:00"
n_cpu="16"
memory="8GB"

{
	IFS=","
	while read name input_prev input_TS input_next; do
		mkdir ${name}
		export name=$name input_prev=$input_prev input_TS=$input_TS input_next=$input_next walltime=$walltime n_cpu=$n_cpu memory=$memory
		envsubst '$name,$input_prev,$input_TS,$input_next' < TS_search_hi-res.inp > $name/$name.inp
		envsubst '$name,$walltime,$n_cpu,$memory' < orca_template.pbs > $name/$name.pbs
		cp  $input_prev ./$name/
		cp  $input_TS ./$name/
		cp  $input_next ./$name/
		cd $name/
		qsub $name.pbs
		cd ..
	done
} < "$config"
