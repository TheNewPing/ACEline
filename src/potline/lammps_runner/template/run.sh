#!/bin/bash

export OMP_NUM_THREADS=${n_cpu}

echo "start"
start_time=`date +%s`
mpirun --oversubscribe -np ${n_cpu} ${lammps_bin_path} -in ${bench_potential_in_path} -v steps ${prerun_steps}
echo "prerun done"
mid_time=`date +%s`
mpirun --oversubscribe -np ${n_cpu} ${lammps_bin_path} -in ${bench_potential_in_path} -v steps ${max_steps}
end_time=`date +%s`
echo "finished"

runtime1=$((mid_time-start_time))
runtime2=$((end_time-mid_time))
runtime3=$((runtime2-runtime1))

# Write timings to a file
timings_file="${out_path}/bench_timings.csv"
echo "start_time,mid_time,end_time,prerun_steps,max_steps,time_diff" > $timings_file
echo "$start_time,$mid_time,$end_time,${prerun_steps},${max_steps},$runtime3" >> $timings_file

exit 0
