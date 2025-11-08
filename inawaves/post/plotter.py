info = """
================
BMKG-OFS Plotter
================
"""

import os
import logging
import numpy as np
import xarray as xr
from datetime import datetime
from joblib import Parallel, delayed
from libplotter import *

op = plotter()

def run_plot(model, baserun, tsel, ds, var, area_name, out_dir, depth=None):
    # logging.info(f"======{var} | {area_name} | baserun: {baserun} | forecast: {forecast}======")
    if model == 'inawaves':
        ds = ds.isel(time=tsel)
        forecast = pd.to_datetime(ds.time.data)
        op.plot_wave(
            ds=ds,
            var=var,
            area='wilpro',
            wilpel_name=area_name,
            out_dir=out_dir,
            baserun=baserun,
            forecast=forecast,
        )
    elif model == 'inaflows':
        ds = ds.isel(time=tsel)
        forecast = pd.to_datetime(ds.time.data)
        ds = ds.sel(depth=depth)
        op.plot_flow(
            ds=ds,
            var=var,
            area='wilpro',
            wilpel_name=area_name,
            out_dir=out_dir,
            baserun=baserun,
            forecast=forecast,
            depth=depth,
        )
    param = mapCollection(var)
    timeinfo = pd.to_datetime(ds.time.data)
    file_name = timeinfo.strftime(f"{out_dir}/{area_name.lower().replace(" - ", "_").replace(".", "").replace(" ", "_")}/{param.savename}_%Y%m%d%H.png") # type: ignore
    logging.info(f"File saved at {file_name}")

def main(model, baserun:datetime, out_dir=False):
    timenow = datetime.utcnow()
    log_dir = timenow.strftime(f"/home/model-admin/logs/inawaves/%Y/%m/%Y%m%d")
    log_file = timenow.strftime(f"{log_dir}/plotting_{model}_%Y%m%d_%H.log")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(f"{log_file}"),
            logging.StreamHandler()
        ],
        level=logging.INFO
    )

    logging.info(info)    
    wavevar = ['ws', 'swh', 'mwh', 'psh', 'wmp', 'wml', 'psp', 'wsh', 'wsp']
    flowvar = ['csd', 's', 'st', 'sl']
    depthlist = [0, 10, 25, 50, 100, 250]

    logging.info(f"======Running plotter for {model}======")
    if model == 'inawaves':
        filepath = baserun.strftime("/home/model-admin/ofs-prod/inawaves/post/w3g_hires_%Y%m%d_%H00.nc")
        if not out_dir:
            out_dir = baserun.strftime("/data/ofs/output/img/inawaves/%Y/%m/%Y%m%d%H")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        logging.info("======Opening data======")
        ds = xr.open_dataset(filepath, engine='netcdf4')
        timelist = np.arange(0,len(ds.time.data),1)
        ds['uwnd'] = ds['uwnd'].fillna(0.0)
        ds['vwnd'] = ds['vwnd'].fillna(0.0)
        ds['hs'] = ds['hs'].fillna(0.0)
        ds['hmax'] = ds['hmax'].fillna(0.0)
        ds['t01'] = ds['t01'].fillna(0.0)
        ds['lm'] = ds['lm'].fillna(0.0)
        Parallel(n_jobs=48)(
            delayed(
                run_plot
            )(
                model=model,
                baserun=baserun,
                tsel=tsel,
                ds=ds,
                var=var,
                area_name=sta,
                out_dir=out_dir
            )
            for tsel in timelist
            for var in wavevar
            for sta in wilprolist
        )
    elif model == 'inaflows':
        filepath = baserun.strftime("/data/ofs/output/nc/inaflows/%Y/%m/InaFlows_%Y%m%d_%H00.nc")
        out_dir = baserun.strftime("/data/ofs/output/img/inaflows/%Y/%m/%Y%m%d%H")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        logging.info("======Opening data======")
        ds = xr.open_dataset(filepath, engine='netcdf4')
        timelist = np.arange(0,len(ds.time.data),1)
        Parallel(n_jobs=48)(
            delayed(
                run_plot
            )(
                model,
                baserun,
                tsel,
                ds,
                var,
                sta,
                out_dir,
                depth
            )
            for tsel in timelist
            for var in flowvar
            for sta in wilprolist
            for depth in depthlist
        )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="BMKG-OFS Plotter",
        epilog="Example:python plotter.py inawaves 2024102000"
    )
    parser.add_argument("model", help="Model. options: inawaves and inaflows")
    parser.add_argument("modelcycle", help="Baserun to process. format: YYYYMMDDHH")
    parser.add_argument("--out_dir", help="Output directory.")
    args = parser.parse_args()
    baserun = datetime.strptime(args.modelcycle, "%Y%m%d%H")
    main(args.model, baserun, args.out_dir)