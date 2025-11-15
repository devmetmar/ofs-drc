#!/bin/bash
#SBATCH --job-name=WW3OFS
#SBATCH --nodes=8
#SBATCH --time=01:00:00
#SBATCH --ntasks-per-node=12
#SBATCH --cpus-per-task=8
#SBATCH --export=ALL
#SBATCH --distribution=block:block
#SBATCH --exclude=drc0
#SBATCH --exclusive
#SBATCH -o slurm_ww3ofs_%j.out

module purge
module load compiler/2022.0.2
module load mpi/2021.5.1

source ${HOME}/ofs-prod/inawaves/env.sh

set -e

export SLURM_CPU_BIND=NONE

# MPI
export I_MPI_FABRICS=shm:ofi
export I_MPI_SHM=clx_avx2

# OpenMP
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# cpu bind : none rank cores threads
export bull_bind_val=cores

echo "SLURM_NTASKS $SLURM_NTASKS"
echo "SLURM_NTASKS_PER_NODE $SLURM_NTASKS_PER_NODE"
echo "SLURM_CPUS_PER_TASK $SLURM_CPUS_PER_TASK "
echo "SLURM OPENMP NUM THREADS $OMP_NUM_THREADS "
echo "SLURM CPU BIND  ${bull_bind_val} "

cd ${WDIR}/main
ldd ${WDIR}/main/ww3_multi
srun --cpus-per-task=$SLURM_CPUS_PER_TASK --cpu-bind=${bull_bind_val} ${WDIR}/main/ww3_multi
srun --cpus-per-task=$SLURM_CPUS_PER_TASK --cpu-bind=${bull_bind_val} bash -c 'echo -n "task $SLURM_PROCID (node $SLURM_NODEID): "; taskset -cp $$' | sort -k 6

echo "Finish model integration ..."
exit 0
