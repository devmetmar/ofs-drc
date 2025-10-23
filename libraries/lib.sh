***REMOVED***

set -e  # stop on error

export nproc=32

module purge
module load icc/2022.0.2
export CC=icc
export CXX=icpc
export CFLAGS='-O2 -fPIC'
export CPPFLAGS=''
PREFIX=/home/model-admin/ofs-prod/libraries

cd $PREFIX/build
echo "Installing OpenSSL (required for CMake HTTPS support)"
wget https://www.openssl.org/source/openssl-1.1.1k.tar.gz
tar -xf openssl-1.1.1k.tar.gz
cd openssl-1.1.1k
./config --prefix=$PREFIX --openssldir=$PREFIX/ssl shared zlib > $PREFIX/build/openssl_build.log 2>&1
make -j$(nproc) >> $PREFIX/build/openssl_build.log 2>&1
make install >> $PREFIX/build/openssl_build.log 2>&1

module purge
module load compiler/2022.0.2
module load mpi/2021.5.1
export FC=mpiifort
export CC=mpiicc
export CXX=mpiicpc
export FFLAGS='-O3 -xHost -ipo -fpp' #Interprocedural optimization & Fortran preprocessor, only for fortran as it heavy use in WW3
export CFLAGS='-O3 -xHost -ipo'   #Interprocedural optimization
export CXXFLAGS='-O3 -xHost'

PREFIX=/home/model-admin/ofs-prod/libraries
export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH
***REMOVED***

cd $PREFIX/build
echo "Installing CMAKE"
wget https://github.com/Kitware/CMake/releases/download/v3.31.0-rc1/cmake-3.31.0-rc1.tar.gz
tar -xzvf cmake-3.31.0-rc1.tar.gz
cd cmake-3.31.0-rc1
./configure \
    --prefix=$PREFIX --parallel=8 > $PREFIX/build/cmake_build.log 2>&1
make -j $(nproc) >> $PREFIX/build/cmake_build.log 2>&1
make install >> $PREFIX/build/cmake_build.log 2>&1
export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH

cd $PREFIX/build
echo "Installing zlib"
wget https://www.zlib.net/fossils/zlib-1.3.1.tar.gz
tar -xzvf zlib-1.3.1.tar.gz
cd zlib-1.3.1
./configure --prefix=$PREFIX > $PREFIX/build/zlib_build.log 2>&1
make -j $(nproc) >> $PREFIX/build/zlib_build.log 2>&1
make install >> $PREFIX/build/zlib_build.log 2>&1
export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH

cd $PREFIX/build
echo "Installing HDF-5"
wget https://support.hdfgroup.org/ftp/HDF5/releases/hdf5-1.13/hdf5-1.13.0/src/hdf5-1.13.0.tar.gz
tar -xzvf hdf5-1.13.0.tar.gz
cd hdf5-1.13.0 
./configure --enable-fortran --enable-parallel \
    --prefix=$PREFIX \
    CPPFLAGS="-I$PREFIX/include" \
    LDFLAGS="-L$PREFIX/lib" > $PREFIX/build/hdf5_build.log 2>&1
make -j $(nproc) >> $PREFIX/build/hdf5_build.log 2>&1
make install >> $PREFIX/build/hdf5_build.log 2>&1
export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH

cd $PREFIX/build
echo "Installing netcdf-c"
wget https://downloads.unidata.ucar.edu/netcdf-c/4.9.2/netcdf-c-4.9.2.tar.gz
tar -xzvf netcdf-c-4.9.2.tar.gz
cd netcdf-c-4.9.2
./configure --enable-netcdf-4 --disable-byterange --disable-libxml2 \
    --prefix=$PREFIX \
    CPPFLAGS="-I$PREFIX/include" \
    LDFLAGS="-L$PREFIX/lib" > $PREFIX/build/ncc_build.log 2>&1
make -j $(nproc) >> n$PREFIX/build/cc_build.log 2>&1
make install >> $PREFIX/build/ncc_build.log 2>&1
export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH

cd $PREFIX/build
echo "Installing netcdf-fortran"
wget https://downloads.unidata.ucar.edu/netcdf-fortran/4.6.1/netcdf-fortran-4.6.1.tar.gz
tar -xzvf netcdf-fortran-4.6.1.tar.gz
cd netcdf-fortran-4.6.1
./configure --enable-parallel-tests \
    --prefix=$PREFIX \
    CPPFLAGS="-I$PREFIX/include" \
    LDFLAGS="-L$PREFIX/lib" > $PREFIX/build/ncf_build.log 2>&1
make -j $(nproc) >> $PREFIX/build/ncf_build.log 2>&1
make install >> $PREFIX/build/ncf_build.log 2>&1
export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH

cd $PREFIX/build
echo "Installing netcdf-cxx"
wget https://downloads.unidata.ucar.edu/netcdf-cxx/4.3.1/netcdf-cxx4-4.3.1.tar.gz
tar -xzvf netcdf-cxx4-4.3.1.tar.gz
cd netcdf-cxx4-4.3.1
./configure \
    --prefix=$PREFIX \
    CPPFLAGS="-I$PREFIX/include" \
    LDFLAGS="-L$PREFIX/lib" > $PREFIX/build/nccx_build.log 2>&1
make -j $(nproc) >> $PREFIX/build/nccx_build.log 2>&1
make install >> $PREFIX/build/nccx_build.log 2>&1
export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH
echo "✅ All libraries installed successfully in $PREFIX"
