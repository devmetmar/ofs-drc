#!/bin/bash
set -e  # stop on first error
set -o pipefail

echo ">>> Loading modules"
module purge
module load compiler/2022.0.2
module load mpi/2021.5.1

echo ">>> Setting compiler environment"
export CC=mpiicc
export CXX=mpiicpc
export FC=mpiifort
export F90=mpiifort

echo ">>> Setting paths for libraries"
export LIBRARIES=/home/model-admin/ofs-prod/libraries
export PATH=$LIBRARIES/bin:$PATH
export LD_LIBRARY_PATH=$LIBRARIES/lib:$LD_LIBRARY_PATH
export LIBRARY_PATH=$LIBRARIES/lib:$LIBRARY_PATH
***REMOVED***
export CPATH=$LIBRARIES/include:$CPATH
export HDF5_ROOT=$LIBRARIES
export NETCDF_ROOT=$LIBRARIES
export NETCDF_FORTRAN_ROOT=$LIBRARIES
export WW3DIR=/home/model-admin/ofs-prod/inawaves/WW3
export nproc=32

echo ">>> Setting compiler flags for AMD EPYC (Intel compiler)"
export FFLAGS="-O3 -march=core-avx2 -fpp -fp-model precise -qopt-report=5 -qopt-report-phase=vec"
export CFLAGS="-O3 -march=core-avx2"
export CXXFLAGS="-O3 -march=core-avx2"

echo ">>> Cloning and preparing WW3"
if [ ! -d $WW3DIR ]; then
    echo ">>> WW3 directory not found, cloning from NOAA-EMC repository"
    git clone https://github.com/NOAA-EMC/WW3.git
fi
cd $WW3DIR
rm -rf build
mkdir build && cd build
rm -f CMakeCache.txt

echo ">>> Running CMake"
cmake .. \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_Fortran_COMPILER=${FC} \
    -DCMAKE_Fortran_FLAGS="${FFLAGS}" \
    -DSWITCH=OFS \
    -DNETCDF_PATH=$LIBRARIES \
    -DHDF5_PATH=$LIBRARIES \
    -DCMAKE_INSTALL_PREFIX=$WW3DIR/build

echo ">>> Building WW3 with $(nproc) cores"
make -j $(nproc) VERBOSE=1

echo ">>> Copying executables to model bin directory"
cp -v $WW3DIR/build/bin/* $WW3DIR/model/bin

echo ">>> Done! WW3 successfully built and installed."