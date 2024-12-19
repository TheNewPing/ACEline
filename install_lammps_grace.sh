#!/bin/bash
#SBATCH --job-name=lmp_inst
#SBATCH --output=lmp_inst_%j.out
#SBATCH --error=lmp_inst_%j.err
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
#SBATCH --mem=20G

module load 2023
module load OpenMPI/4.1.5-NVHPC-24.5-CUDA-12.1.1

source $(conda info --base)/etc/profile.d/conda.sh
conda activate grace

cd lammps_grace
cd lammps

if [ -d "build" ]; then
      rm -rf build
fi

mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=Release \
      -D BUILD_MPI=ON \
      -D PKG_ML-PACE=ON \
      -D PKG_MC=ON \
      ../cmake
cmake --build . -- -j 32