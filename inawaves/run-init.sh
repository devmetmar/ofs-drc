#!/bin/bash
module purge
module load mpi/2021.5.1
module load compiler/2022.0.2
source ${HOME}/ofs-prod/inawaves/env.sh
log_file="$WDIR/inawaves_init.log"
function logging() {
        echo "`date "+%Y-%m-%d %H:%M:%S"` : $1" >> $log_file
}

logging "Initialize GFS ..."
cd $INDATA/static/gfs
ln -sf $WW3DIR/model/bin/ww3_grid .
./ww3_grid > $log_file 2>&1 # the output is mod_def.ww3
wait
ln -sf $INDATA/static/gfs/mod_def.ww3 $INDATA/static/gfs/mod_def.gfs

logging "Initialize GLOBAL Domain ..."
cd $INDATA/static/global
ln -sf $WW3DIR/model/bin/ww3_grid .
cp ${SRCTMP}/global/ww3_grid.inp .
cp ${SRCTMP}/global/global* .
./ww3_grid >> $log_file 2>&1
wait
ln -sf $INDATA/static/global/mod_def.ww3 $INDATA/static/global/mod_def.global

logging "Initialize REG Domain ..."
cd $INDATA/static/reg
ln -sf $WW3DIR/model/bin/ww3_grid .
cp ${SRCTMP}/reg/ww3_grid.inp .
cp ${SRCTMP}/reg/reg* .
./ww3_grid >> $log_file 2>&1
wait
ln -sf $INDATA/static/reg/mod_def.ww3 $INDATA/static/reg/mod_def.reg

logging "Initialize SREG Domain ..."
cd $INDATA/static/sreg
ln -sf $WW3DIR/model/bin/ww3_grid .
cp ${SRCTMP}/sreg/ww3_grid.inp .
cp ${SRCTMP}/sreg/sreg* .
./ww3_grid >> $log_file 2>&1
wait
ln -sf $INDATA/static/sreg/mod_def.ww3 $INDATA/static/sreg/mod_def.sreg

logging "Initialize HIRES Domain ..."
cd $INDATA/static/hires
ln -sf $WW3DIR/model/bin/ww3_grid .
cp ${SRCTMP}/hires/ww3_grid.inp .
cp ${SRCTMP}/hires/href* .
./ww3_grid >> $log_file 2>&1
wait
ln -sf $INDATA/static/hires/mod_def.ww3 $INDATA/static/hires/mod_def.hires

logging "Initialize POINTS Domain ..."
cd $INDATA/static/points
ln -sf $WW3DIR/model/bin/ww3_grid .
cp ${SRCTMP}/points/ww3_grid.inp .
./ww3_grid >> $log_file 2>&1
wait
ln -sf $INDATA/static/points/mod_def.ww3 $INDATA/static/points/mod_def.points

logging "Linking Binary files ..."
ln -sf $WW3DIR/model/bin/ww3_prep $WDIR/prep
ln -sf $WW3DIR/model/bin/ww3_multi $WDIR/main
ln -sf $WW3DIR/model/bin/gx_outf $WDIR/post
cp ${SRCTMP}/gfs/ww3_prep.inp ${WDIR}/prep

logging "Finish INAWAVES Initialization."