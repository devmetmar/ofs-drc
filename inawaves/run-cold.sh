***REMOVED***
# 
# WW3 DRC COLD START WRAPPER SCRIPT
#
#  ---> How to use this script:
#       
#       /bin/bash run-cold.sh YYYYMMDDHH <yes>
#     
#       - First argument for the model start date
#       - Second argument for fast mode without confirmation prompt
#       - The default restart is 3 days from the start date. To change this, edit the DRestart variable in this script.
#       - Example:
#           /bin/bash run-cold.sh 2023111500 yes
#
# IMPORTANT NOTES IN RUNNING SLURM ON DRC
# - /data is not accessible from compute node
# - Avoid running SLURM command in relation with accessing/linking to /data
# 
# Created in November 2025
# Contact: tyo.suwignyo@gmail.com

set -e
source /etc/profile.d/modules.sh
module purge
module load mpi/2021.5.1
module load compiler/2022.0.2
source ${HOME}/ofs-prod/inawaves/env.sh
start_time=$(date +%s)
time_start=$(date --date "@${start_time}" +"%Y-%m-%d %H:%M:%S")
function logging() {
        echo "`date "+%Y-%m-%d %H:%M:%S"` : $1" >> $log_file
}
on_error() {
    local last_status=$?
    local last_line=${BASH_LINENO[0]}
    local last_cmd="${BASH_COMMAND}"
    local errmsg="WW3 DRC ERROR! Script stopped at line $last_line with exit code $last_status.
Failed command: $last_cmd
Cycle: ${NWDAY}${CYCLE}
Log: $log_file"
    logging "$errmsg"
    exit $last_status
}

trap 'on_error' ERR

# Create DTN and overide input
if [[ $2 == "yes" ]];then
        echo "Fast mode, overide date: $1"
        tstart=$1
        NWDAY=${tstart:0:8}
        CYCLE=${tstart:8:2}
elif ! [ -z "$1" ];then
        echo "Press y to confirm the run date : $1"
        read -n 1 k
        if [[ $k != "y" ]];then
                echo "Aborting"
                exit 1
        fi
        tstart=$1
        NWDAY=${tstart:0:8}
        CYCLE=${tstart:8:2}
else
    	NWDAY=`date -u +%Y%m%d`
        CYCLE=`${WDIR}/prep/getcyc.sh`
fi

DRestart='3'
NWDAY_R=`date -u -d "${NWDAY} ${CYCLE} UTC + ${DRestart} days" +%Y%m%d`
CYCLE_R=${CYCLE}
year=${NWDAY:0:4}
month=${NWDAY:4:2}
day=${NWDAY:6:2}
log_dir="${HOME}/logs/inawaves/$year/$month/$year$month$day"
log_file="$log_dir/w3g_cold_${NWDAY}_${CYCLE}.log"
if [ ! -d "$log_dir" ]; then
    mkdir -p "$log_dir"
    echo "Directory $log_dir created"
else
    echo "Directory $log_dir already exists"
fi

if [ ! -f "$log_file" ]; then
    touch "$log_file"
    echo "Log file $log_file created"
else
    echo "Log file $log_file already exists"
fi

check_job_status() {
    local job_id=$1
    job_status=$(sacct -j $job_id --format=State --noheader | grep -E "RUNNING|PENDING")
    job_status=$(sacct -X -n -o State --j $job_id | grep -E "RUNNING|PENDING")
    job_status=$(echo "${job_status}" | tr -d ' ')
    echo "${job_status}"
}

logging "########################################################################"
logging "                       WRAPPER FOR INAWAVES MODEL                      "
logging "------------------------------------------------------------------------"
logging "T0             : ${NWDAY} - ${CYCLE}"
logging "RESTART FILES  : ${NWDAY_R} - ${CYCLE_R}"
logging "ROOTDIR        : ${RDIR}"
logging "WORKDIR        : ${WDIR}"
logging "LIBRARIES      : ${LIBRARIES}"
logging "PYTHONPATH     : $(which python)"
logging "INDATA         : ${INDATA}"
logging "OUTDATA        : ${OUDATA}"
logging "LOGFILE        : ${log_file}"
logging "PATH           : ${PATH}"
logging "LD_LIBRARY_PATH: ${LD_LIBRARY_PATH}"
logging "########################################################################"


logging "------------------------------------------------------------------------"
logging "                             PREPROCESSING                              "
logging "------------------------------------------------------------------------"

${PYTHON} -u ${WDIR}/prep/grib2ww3.py -t 384 ${INDATA}/gfs ${INDATA}/gfs/w3g_gfs.txt archive ${NWDAY}${CYCLE} >> $log_file 2>&1

rm -rf ${WDIR}/prep/wind.txt
rm -rf ${WDIR}/prep/mod_def*
cp -f ${INDATA}/gfs/w3g_gfs.txt ${WDIR}/prep/wind.txt --verbose >> $log_file 2>&1
cp -f ${INDATA}/static/gfs/mod_def.ww3 ${WDIR}/prep/mod_def.ww3 --verbose >> $log_file 2>&1
cd ${WDIR}/prep
logging "PATH           : $PATH"
logging "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
srun --ntasks=1 --exclude=drc0 --exclusive ${WDIR}/prep/ww3_prep >> $log_file 2>&1
cd ${WDIR}/main
rm -rf ${WDIR}/main/wind.gfs
ln -sf ${WDIR}/prep/wind.ww3 ${WDIR}/main/wind.gfs

logging "------------------------------------------------------------------------"
logging "                           MODEL INTEGRATION                            "
logging "------------------------------------------------------------------------"
cd ${WDIR}/main
STime="${NWDAY} ${CYCLE}"
ETime=$(date +"%Y%m%d %H%M" -d "${STime} + ${DRestart}Days")
ResTime=`date +"%Y%m%d %H%M" -d "${STime} + ${DRestart}Days"`

logging "Start time $STime"
logging "End time $ETime"
logging "Restart time $ResTime"

sed "
    s|tgl_start|${STime}|
    s|tgl_end|${ETime}|
    s|tgl_restart|${ResTime}|
    s|tgl_restart|${ResTime}|
    " "${INDATA}/templates/ww3_multi_gfs.inp" > "${WDIR}/main/ww3_multi.inp"

if [ $? -eq 0 ]; then
    logging "Success editing ww3_multi.inp"
else
    logging "Failed editing ww3_multi.inp"
    exit 1
fi

logging "Removing old restart files ..."
rm -rf ${WDIR}/main/restart*

logging "Copying mod_def files ..."
rm -rf ${WDIR}/main/mod_def*
cp -f ${INDATA}/static/gfs/mod_def.ww3 ${WDIR}/main/mod_def.gfs --verbose >> $log_file 2>&1
cp -f ${INDATA}/static/global/mod_def.ww3 ${WDIR}/main/mod_def.global --verbose >> $log_file 2>&1
cp -f ${INDATA}/static/reg/mod_def.ww3 ${WDIR}/main/mod_def.reg --verbose >> $log_file 2>&1
cp -f ${INDATA}/static/sreg/mod_def.ww3 ${WDIR}/main/mod_def.sreg --verbose >> $log_file 2>&1
cp -f ${INDATA}/static/hires/mod_def.ww3 ${WDIR}/main/mod_def.hires --verbose >> $log_file 2>&1
cp -f ${INDATA}/static/points/mod_def.ww3 ${WDIR}/main/mod_def.points --verbose >> $log_file 2>&1

logging "PATH           : ${PATH}"
logging "LD_LIBRARY_PATH: ${LD_LIBRARY_PATH}"
logging "Submitting job run_multi.sh ..."
job_id=$(sbatch ${WDIR}/main/run_ww3multi.sh ${NWDAY}${CYCLE} | awk '{print $4}')
logging "Job ID: $job_id"

sleep 10

# Check if the job ID was captured successfully
if [ -z "$job_id" ]; then
    logging "Failed to submit the job."
    exit 1
fi

while true; do
    job_status=$(check_job_status $job_id)
    logging "Job status: ${job_status}"  # Debug output
    if [ "${job_status}" == "" ]; then
        logging "ww3_multi job $job_id has completed."
        break
    fi
    logging "ww3_multi job $job_id is still running. Checking again in 60 seconds..."
    sleep 60
done

logging "Model integration has finished."
cat log.mww3 >> $log_file
mv slurm* ${log_dir} >> $log_file 2>&1

logging "Moving restart files to each domain directory ..."
mv ${WDIR}/main/restart001.global ${INDATA}/static/global/restart.ww3 >> $log_file 2>&1 
mv ${WDIR}/main/restart001.reg    ${INDATA}/static/reg/restart.ww3 >> $log_file 2>&1    
mv ${WDIR}/main/restart001.sreg   ${INDATA}/static/sreg/restart.ww3 >> $log_file 2>&1   
mv ${WDIR}/main/restart001.hires  ${INDATA}/static/hires/restart.ww3 >> $log_file 2>&1  

end_time=$(date +%s)
time_end=$(date --date "@${end_time}" +"%Y-%m-%d %H:%M:%S")
elapsed_time=$((end_time - start_time))

logging "########################################################################"
logging "          SUCCESSFULLY GENERATING RESTART FILES                         "
logging "------------------------------------------------------------------------"
logging "Total elapsed time: ${elapsed_time} seconds                             "
logging "Start time       : ${time_start}                                        "
logging "End time         : ${time_end}                                          "
logging "Exiting                                                                 "
logging "########################################################################"

exit 0
