#!/bin/bash
# Desc    : script library to define last GFS cycle based on 
#           now time
# -----------------------------------------------------------------
# Usage   : ./getcyc 
# -----------------------------------------------------------------
# Author  : I Dewa Gede A. Junnaedhi - WCPL ITB 2013
# Revision: 2013/11/29 - First created
# ==================================================================
# Check if bc command exist

# Filter arguments
if [ "$#" -gt "0" ]; then
    echo ""
    echo "Error: no arguments needed"
    cat $0 | sed -n '/^# --------/,/^# ----------/ p' | sed -e 's/^#//'
    echo "aborting..."
    exit 1
fi

HH=`date -u +%H | bc`
if [ "$HH" -ge "3" ] && [ "$HH" -lt "15" ]; then
	echo "00"
else
	echo "12"
fi
# Terminate script
exit 0
