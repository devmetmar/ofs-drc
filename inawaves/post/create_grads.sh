#!/bin/bash

set -euo pipefail

# Load module system for non-interactive shells
source /etc/profile.d/modules.sh

# Purge modules and load necessary ones
module purge
module load mpi/2021.5.1
module load compiler/2022.0.2
source ${HOME}/ofs-prod/inawaves/env.sh

# Loop through model types
for n in global reg hires; do

    echo ">>> Processing model: $n"

    # Remove symlinks if exist
    rm -f out_grd.ww3 mod_def.ww3

    # Create required symlinks
    ln -s "mod_def.${n}" mod_def.ww3
    ln -s "out_grd.${n}" out_grd.ww3

    # Run gx_outf executable
    ${WDIR}/post/gx_outf

    # Rename and update output files
    mv ww3.grads "${n}.grads"
    sed -e "s/ww3.grads/${n}.grads/g" ww3.ctl > "${n}.ctl"

    echo ">>> Completed ${n}"
done

echo ">>> All processing complete."
