#!/bin/bash

RDIR="/home/model-admin/ofs-prod"
WDIR="${RDIR}/inawaves"
WW3DIR="$WDIR/WW3"
LIBRARIES="${RDIR}/libraries"
PYTHON="/home/model-admin/opt/miniforge3/envs/ofs/bin/python"
INDATA="/data/ofs/input"
OUDATA="/data/ofs/output"
SCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SRCTMP="/tmp/inawaves-prod"
TELEGRAM_BOT_TOKEN="6184213398:AAGz6Mwxn04Fsh7-hw412NBa-fBP5ABzs8I"
TELEGRAM_CHAT_ID="-1001911911907"

export PATH=${LIBRARIES}/bin:$PATH
export LD_LIBRARY_PATH=${LIBRARIES}/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/lib64:$LD_LIBRARY_PATH
export NetCDF_ROOT=${LIBRARIES}/bin
export NetCDF_INCLUDE_DIRS=${LIBRARIES}/include