#!/bin/bash

module purge
module load compiler/2022.0.2
module load mpi/2021.5.1

export CC=mpiicc
export CXX=mpiicpc
export FC=mpiifort
export F90=mpiifort
export NetCDF_ROOT=/home/dev-001/libraries/bin
export NetCDF_INCLUDE_DIRS=/home/dev-001/libraries/include
export PATH=/home/dev-001/libraries/bin:$PATH
export LD_LIBRARY_PATH=/home/dev-001/libraries/lib:$LD_LIBRARY_PATH
export LIBRARY_PATH=/home/dev-001/libraries/lib:$LIBRARY_PATH
export LD_LIBRARY_PATH=/lib64:$LD_LIBRARY_PATH

git clone https://github.com/NOAA-EMC/WW3.git && mv WW3/* . && rm -rf WW3
rm -rf build
mkdir build && cd build
rm -f CMakeCache.txt
cmake .. -DSWITCH=hybrid_omph -DCMAKE_INSTALL_PREFIX=~/ww3/build
make -j 32 VERBOSE=1
cp ~/ww3/build/bin/* ~/ww3/model/bin