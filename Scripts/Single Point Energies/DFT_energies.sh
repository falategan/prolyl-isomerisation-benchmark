#!/bin/bash

walltime="24:00:00"
n_cpu="16"
memory="8GB"


{	
	IFS=";"
	while read method basis; do
		{
			while read geometry; do
				input=${geometry}.xyz
				name=${geometry}_${method}_${basis}
				name="${name// /_}"
				name="${name%_*/C}"
				echo ${name}
				mkdir ${name}
				export name=$name input=$input method=$method basis=$basis walltime=$walltime n_cpu=$n_cpu memory=$memory
				envsubst '$name,$input,$method,$basis' < DFT_energies.inp > $name/$name.inp
				envsubst '$name,$walltime,$n_cpu,$memory' < orca_template.pbs > $name/$name.pbs
				cp ${input} ./$name/
				cd $name/
				qsub $name.pbs
				cd ..
		done
		} < geometries.config
	done
} < DFT_LoT.config


