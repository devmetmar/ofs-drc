"""
Toolkit for Plotter

Ocotober 2024

Created by: Tyo Pusmar
email: suwignyo.prasetyo@bmkg.go.id
"""

import os
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import geopandas as gpd
import cartopy.crs as ccrs
from matplotlib.offsetbox import (AnchoredOffsetbox, HPacker, TextArea, OffsetImage)
from cartopy.feature import LAND, COASTLINE, BORDERS, GSHHSFeature, ShapelyFeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from matplotlib.colors import LinearSegmentedColormap
import cartopy.io.img_tiles as cimgt
import cartopy
import matplotlib.ticker as mticker
from matplotlib.ticker import FuncFormatter
import traceback

class plotter:
    """
    Plotter for BMKG-OFS
    """
    def __init__(
        self
    ):
        pass

    def __format_tick__(self, x, pos):
        return f'{x:g}'

    def __plot_spasial__(
        self,
        baserun,
        forecast,
        lat_data: np.ndarray, 
        lon_data: np.ndarray, 
        latlon_interval: float, 
        color_map, 
        level: list[float], 
        magnitude: xr.DataArray, 
        u_comp: xr.DataArray, 
        v_comp: xr.DataArray, 
        skip: int, 
        scale: int, 
        dirtitle: str,
        map_title: str, 
        legend: str, 
        file_name: str,
        plot_shapefile: bool,
        shp: str,
        googleplot: bool = False,
        zoom4google:int = 1,
        plotloc: bool = False,
        liloc: tuple[list[float], list[float], list[str]] = None,
    ) -> bool:
        """
        2D Plotter, Spatial maps
        """

        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(10, 10))
        
        # Plot parallels and meridians
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.2, color='w') # type: ignore
        gl.top_labels = False
        gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 7}
        gl.ylabel_style = {'size': 7}
        # cmap = color_map
        # try:
        #     cmap = LinearSegmentedColormap.from_list('custom_map', color_map)
        # except:
        #     cmap = color_map
        bounds = level
        # norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N) # type: ignore
        
        if googleplot:
            google: cartopy.io.img_tiles.GoogleTiles = cimgt.GoogleTiles(style='satellite') # type: ignore
            zoom = zoom4google
            scale = np.ceil(-np.sqrt(2)*np.log(np.divide(zoom,350.0)))
            ax.add_image(google, int(scale), zorder=0) # type: ignore
        else:
            ax.add_feature(BORDERS, linewidth=1, zorder=4) # type: ignore
            ax.add_feature(LAND, edgecolor='black', facecolor='gray', zorder=3) # type: ignore
            ax.add_feature(COASTLINE, linewidth=1) # type: ignore
            
        if u_comp is not None:
            cmap = LinearSegmentedColormap.from_list('custom_map', color_map)
            norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N) # type: ignore
            cmap.set_over('indigo')
            wv_map = ax.contourf(
                lon_data, 
                lat_data, 
                magnitude, 
                # cmap=cmap, 
                colors=color_map,
                norm=norm, 
                levels=bounds, 
                transform=ccrs.PlateCarree(), 
                zorder=1, 
                extend='max'
            )
            ax.quiver(
                lon_data[::skip], 
                lat_data[::skip], 
                u_comp[::skip, ::skip], 
                v_comp[::skip, ::skip], 
                units='inches', 
                scale=scale, 
                pivot='mid', 
                width=0.01, 
                headwidth=5.5,
                headlength=6,
                headaxislength=4,
                minlength=1,
                minshaft=1,
                transform=ccrs.PlateCarree(), 
                zorder=1
            )

        if u_comp is None:
            cmap = LinearSegmentedColormap.from_list('custom_map', color_map)
            norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N) # type: ignore
            cmap.set_over('indigo')
            cmap.set_under('indigo')
            wv_map = ax.contourf(
                lon_data, 
                lat_data, 
                magnitude, 
                cmap=cmap, 
                # colors=color_map,
                norm=norm, 
                levels=bounds, 
                transform=ccrs.PlateCarree(), 
                zorder=1, 
                extend='both'
            )

        # if plot_shapefile==True:
        #     try:
        #         gdf_plot=gpd.read_file(f'{shp}.shp')
        #         ax = gdf_plot.plot(ax=ax, edgecolor="black", linewidth=1)
        #     except:
        #         gdf_plot=shp
        #         ax = gdf_plot.plot(ax=ax, edgecolor="black", linewidth=1) # type: ignore

        gdf_plot=shp
        # ax = gdf_plot.plot(ax=ax, edgecolor="black", linewidth=1.5) # type: ignore
        ax.add_feature(ShapelyFeature( # type: ignore
            gdf_plot, 
            ccrs.PlateCarree(), edgecolor='black', facecolor='none'), 
            linewidth=1, zorder=1)

        if plotloc:
            for i, (x, y, label) in enumerate(zip(liloc)): # type: ignore
                ax.scatter(x, y, color='red', s=60, zorder=2)
                ax.annotate(label, (x, y), xytext=(5, -5), textcoords='offset points', fontsize=15)  # Adjust offset as needed

        # Text Section
        logobox = OffsetImage(plt.imread('/data/ofs/input/img/logo60k.png'),zoom=0.5)
        varbox = TextArea(
            f"BADAN METEOROLOGI KLIMATOLOGI DAN GEOFISIKA\n{map_title}",
            textprops=dict(
                color="k", 
                weight='bold',
                family='monospace'
            )
        )
        time_delta = (forecast - baserun).total_seconds()/3600
        initime = f'Initial: {baserun.strftime("%HUTC %Y-%m-%d")}'
        if forecast == baserun:
            fcstime = f'Analysis: {forecast.strftime("%HUTC %Y-%m-%d")} (t+0)'
        else:
            fcstime = f'Forecast: {forecast.strftime("%HUTC %Y-%m-%d")} (t+{time_delta:g})'
        timebox = TextArea(
            f"{initime}\n{fcstime}",
            textprops=dict(
                color="k", 
                size=9, 
                family='monospace',
                horizontalalignment='right'
            )
        )

        logovarbox = HPacker(children=[logobox, varbox],
                      align="center",
                      pad=0, sep=2)
        timeinfobox = HPacker(children=[timebox],
                      align="center",
                      pad=0, sep=2)

        uleftbox = AnchoredOffsetbox(loc='lower left',
                                         child=logovarbox, pad=0.,
                                         frameon=False,
                                         bbox_to_anchor=(0, 1.),
                                         bbox_transform=ax.transAxes,
                                         borderpad=0.1,)
        urightbox = AnchoredOffsetbox(loc='lower right',
                                         child=timeinfobox, pad=0.,
                                         frameon=False,
                                         bbox_to_anchor=(1., 1.01),
                                         bbox_transform=ax.transAxes,
                                         borderpad=0.1,)

        plt.tick_params(axis='both', which='major', labelsize=4)
        plt.tick_params(axis='both', which='major', labelsize=4)
        ax.add_artist(uleftbox)
        ax.add_artist(urightbox)

        source = f'Source: BMKG Ocean Forecast System (BMKG-OFS)'
        credit = f'Created by Center for Marine Meteorology. \u00A9{datetime.now().year}'
        
        sourcecredittext = TextArea(
            f"{source}\n{credit}",
            textprops=dict(
                color="k", 
                size=5.5, 
                # weight='bold',
                family='monospace',
                horizontalalignment='left'
            )
        )
        sourcecreditbox = HPacker(children=[sourcecredittext],
                        align="center",
                        pad=0, sep=2)
        lleftbox = AnchoredOffsetbox(loc='upper left',
                                        child=sourcecreditbox, pad=0.,
                                        frameon=False,
                                        bbox_to_anchor=(0., -0.06),
                                        bbox_transform=ax.transAxes,
                                        borderpad=0.1,)
        
        plt.tick_params(axis='both', which='major', labelsize=4)
        plt.tick_params(axis='both', which='major', labelsize=4)
        ax.add_artist(lleftbox)
        
        # ==================================================
        # Dynamic colorbar adjustment, thanks to GPT4
        # ==================================================
        
        if u_comp is None:
            fig.canvas.draw()  # Force a redraw to ensure all layout calculations are up to date
            bbox = ax.get_position()
            aspect_ratio = bbox.width / bbox.height
            # left, bottom, width, height
            cbar_width = bbox.width-(bbox.width*0.5)
            cbar_left = bbox.x0 + (bbox.width*0.5)
            cbar_bottom = bbox.y0 - 0.06
            cbar_height = 0.015
            # Create a new axes for the colorbar at the calculated position
            cbar_ax = fig.add_axes([cbar_left-0.1, cbar_bottom, cbar_width+0.1, cbar_height])
            # Create the colorbar with the newly adjusted axes
            cbar = fig.colorbar(wv_map, 
                                cax=cbar_ax, 
                                # boundaries=bounds + [bounds[-1] + 1],  # add an extra bound for the upper limit
                                # values=values,  # set the values for color mapping
                                ticks = level,
                                norm=norm,
                                orientation='horizontal', 
                                pad=0.05,
                                extend='both')
        else:
            fig.canvas.draw()  # Force a redraw to ensure all layout calculations are up to date
            bbox = ax.get_position()
            aspect_ratio = bbox.width / bbox.height
            # left, bottom, width, height
            cbar_width = bbox.width-(bbox.width*0.5)
            cbar_left = bbox.x0 + (bbox.width*0.5)
            cbar_bottom = bbox.y0 - 0.06
            cbar_height = 0.015
            # Create a new axes for the colorbar at the calculated position
            cbar_ax = fig.add_axes([cbar_left, cbar_bottom, cbar_width, cbar_height])
            # Create the colorbar with the newly adjusted axes
            cbar = fig.colorbar(wv_map, 
                                cax=cbar_ax, 
                                # boundaries=bounds + [bounds[-1] + 1],  # add an extra bound for the upper limit
                                # values=values,  # set the values for color mapping
                                ticks = level,
                                norm=norm,
                                orientation='horizontal', 
                                pad=0.05,
                                extend='max')
        # Configure the colorbar's appearance as before
        cbar.set_label(f'{legend}', fontsize=9, fontname='monospace', labelpad=-36)
        cbar.ax.tick_params(labelsize=8)
        cbar.ax.xaxis.set_major_formatter(FuncFormatter(self.__format_tick__))

        if u_comp is not None:
            arrlabel = dirtitle
            cbar_bbox = cbar_ax.get_position()
            arrow_x = cbar_bbox.x0 - 0.06  # Adjust as needed
            arrow_y = cbar_bbox.y0 + (cbar_bbox.height / 2) - 0.01  # Center vertically with the colorbar

            # Draw the arrow indicating the wind vector legend
            fig.text(arrow_x, arrow_y+0.02, arrlabel, fontsize=8, ha='center', va='center')
            arrax = fig.add_axes([arrow_x-0.01,arrow_y-0.008,0.014,0.01], frameon=True)
            arrow_length = 0.02  # Length of the arrow
            arrow_width = 0.005  # Width of the arrow shaft
            head_width = 0.006  # Width of the arrow head
            head_length = 0.01  # Length of the arrow head

            # Since arrow_x_start and arrow_y_start are used as the axes' origin, draw the arrow starting from (0, 0)
            arrax.arrow(0, 0, arrow_length, 0.01, head_width=head_width, head_length=head_length, fc='k', ec='k')
            # arrax.text(arrow_x + 0.06, arrow_y, 'm/s', verticalalignment='center', fontsize=9)
            arrax.axis('off')

        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))
        plt.savefig(file_name, bbox_inches='tight',dpi=100)
        return True

    def __plot_wave_warning__(
        self,
        model,
        lat_data: np.ndarray, 
        lon_data: np.ndarray, 
        latlon_interval: float, 
        color_map: matplotlib.colors.ListedColormap, 
        level: list[float], 
        magnitude: xr.DataArray, 
        map_title: str, 
        map_area: str,
        legend_title: str, 
        file_name: str,
        plot_shapefile: bool,
        shp: str | gpd.GeoSeries,
        googleplot: bool = False,
        zoom4google:int = 9,
    ) -> bool:
        """
        2D Plotter, Wave Warning for Public Friendly
        """

        fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(10, 10))
        
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=0.2, color='w') # type: ignore
        gl.top_labels = False
        gl.right_labels = False
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 7}
        gl.ylabel_style = {'size': 7}
        cmap = color_map
        bounds = level
        # norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N) # type: ignore
        
        if googleplot:
            google: cartopy.io.img_tiles.GoogleTiles = cimgt.GoogleTiles(style='satellite') # type: ignore
            zoom = zoom4google
            scale = np.ceil(-np.sqrt(2)*np.log(np.divide(zoom,350.0)))
            ax.add_image(google, int(scale), zorder=0) # type: ignore
        else:
            ax.add_feature(BORDERS, linewidth=1) # type: ignore
            ax.add_feature(LAND, facecolor='gray', zorder=3) # type: ignore
            # ax.add_feature(COASTLINE, linewidth=1)
            
        plotmap = ax.contourf(
            lon_data, 
            lat_data, 
            magnitude, 
            cmap=color_map, 
            levels=level, 
            transform=ccrs.PlateCarree(), 
            zorder=1
        )
        contourmap = ax.contour(
            lon_data, 
            lat_data, 
            magnitude, 
            levels=level, 
            linewidths=0.01, 
            colors='black', 
            transform=ccrs.PlateCarree(), 
            zorder=1
        )
        # ax.clabel(contourmap, contourmap.levels, inline=True, fontsize=7)

        loc = map_area
        if plot_shapefile==True:
            gdf_plot=shp
            ax.add_feature(ShapelyFeature( # type: ignore
            gdf_plot, 
            ccrs.PlateCarree(), edgecolor='black', facecolor='none'), 
            linewidth=1, zorder=1)
            
        # Text Section
        logobox = OffsetImage(plt.imread('/data/ofs/input/img/logo60k.png'),zoom=0.4)
        varbox = TextArea(
            f"{map_title}",
            textprops=dict(
                color="k", 
                weight='bold',
                family='monospace'
            )
        )
        print(model)
        if model == 'inacawo':
            source = f'Source: INACAWO - 3km'
        else:
            source = f"Source: INAWAVES"
        timebox = TextArea(
            f"{loc}\n{source}",
            textprops=dict(
                color="k", 
                size=7, 
                family='monospace',
                horizontalalignment='right'
            )
        )

        logovarbox = HPacker(children=[logobox, varbox],
                      align="center",
                      pad=0, sep=2)
        timeinfobox = HPacker(children=[timebox],
                      align="center",
                      pad=0, sep=2)

        uleftbox = AnchoredOffsetbox(loc='lower left',
                                         child=logovarbox, pad=0.,
                                         frameon=False,
                                         bbox_to_anchor=(0, 1.),
                                         bbox_transform=ax.transAxes,
                                         borderpad=0.1,)
        urightbox = AnchoredOffsetbox(loc='lower right',
                                         child=timeinfobox, pad=0.,
                                         frameon=False,
                                         bbox_to_anchor=(1., 1.),
                                         bbox_transform=ax.transAxes,
                                         borderpad=0.1,)

        plt.tick_params(axis='both', which='major', labelsize=4)
        plt.tick_params(axis='both', which='major', labelsize=4)
        ax.add_artist(uleftbox)
        ax.add_artist(urightbox)
        
        fig.canvas.draw()
        bbox = ax.get_position()
        aspect_ratio = bbox.width / bbox.height
        cbar_width = 0.02
        cbar_left = bbox.x1 + 0.005
        cbar_bottom = bbox.y0
        cbar_height = bbox.height
        cbar_ax = fig.add_axes([cbar_left, cbar_bottom, cbar_width, cbar_height])
        col_bar1 = fig.colorbar(plotmap, 
                                cax=cbar_ax, 
                                ticks = [round(i,2) for i in level],
                                # format = "{x:.2f}",
                                format = mticker.FixedFormatter(['0 m', '1.25 m', '2.5 m', '4 m', '6 m', '9 m']),
                                # norm=norm,
                                orientation='vertical', 
                                pad=0.05,
                                extend='both')
        col_bar1.ax.tick_params(labelsize=7)
        
        colorbar_ticks = [0.625, 1.875, 3.25, 5.0, 7.5]
        colorbar_labels = ['Tenang -\nRendah', 'Sedang', 'Tinggi', 'Sangat\nTinggi', 'Ekstrem']

        col_bar1.set_ticks(colorbar_ticks, labels=colorbar_labels, minor=True)

        plt.savefig(file_name, bbox_inches='tight',dpi=300)
        return True

    def run_plot(
        self, 
        model, 
        ds:xr.Dataset, 
        var:str, 
        wilpel:str, 
        wilpel_name:str, 
        map_area:str,
        out_dir:str,
        time=None,
        baserun=False,
        forecast:timedelta|bool=False,
        google: bool = False,
        zoom4google:int = 1,
        plotloc: bool = False,
        liloc: tuple[list[float], list[float], list[str]] | None = None,
    ):
        """Runner for Plotter 2D Spasial"""
        if wilpel == 'wilpel':
            wil_name = stamarCollection(wilpel_name)
            latlon_intv = wil_name.ledspace
            arw_intv = wil_name.arrowdensity
            arw_scale = wil_name.sv
            map_area = wil_name.title
            if wilpel_name == 'indonesia':
                plot_shp = False
                shp = None
            else:
                plot_shp = True
                shp = wil_name.shp
        elif wilpel == 'wilpro':
            wil_name = wilproCollection(wilpel_name)
            latlon_intv = wil_name.ledspace
            arw_intv = wil_name.arrowdensity
            arw_scale = wil_name.sv
            plot_shp = True
            shp = wil_name.shp
            map_area = wil_name.title
        else:
            latlon_intv = 1
            arw_intv = 1
            arw_scale = 30
            plot_shp = False
            shp = None

        ds = ds.sel(lon=slice(wil_name.lonbounds[0], wil_name.lonbounds[1]), lat=slice(wil_name.latbounds[0], wil_name.latbounds[1])) # type: ignore
        
        lat = ds['lat'].data
        lon = ds['lon'].data

        param = mapCollection(var)
        # try:
        #     cmap = LinearSegmentedColormap.from_list('custom_map', param.colorbar)
        # except:
        #     cmap = param.colorbar
        cmap = param.colorbar
        lvl = param.clev
    
        if var == 's' or var == 'st' or var == 'sl':
            ucomp = None
            vcomp = None
            mag = ds[param.var1]
        elif var == 'csd':
            ucomp = ds[param.var1]*100
            vcomp = ds[param.var2]*100
            mag = np.sqrt(np.square(ucomp) + np.square(vcomp))
            ucomp, vcomp = 2*ucomp/mag, 2*vcomp/mag
        elif var == 'ws':
            ucomp = ds[param.var1]*1.94384
            vcomp = ds[param.var2]*1.94384
            mag = np.sqrt(np.square(ucomp) + np.square(vcomp))
            ucomp, vcomp = 2*ucomp/mag, 2*vcomp/mag
        else:
            mag = ds[param.var1]
            uvcomp = ds[param.var2]
            ucomp = np.cos(np.deg2rad(uvcomp))
            vcomp = np.sin(np.deg2rad(uvcomp))
            uvcomp = np.arctan2(ucomp, vcomp)
            ucomp = np.cos(uvcomp)
            vcomp = np.sin(uvcomp)
            ucomp, vcomp = 2*ucomp, 2*vcomp

        if not wilpel:
            ucomp, vcomp = 1.3*ucomp/2, 1.3*vcomp/2 # type: ignore
        
        try:
            timeinfo = pd.to_datetime(ds.time.data)
        except:
            timeinfo = time
        file_name = timeinfo.strftime(f"{out_dir}/{param.savename}_%Y%m%d_%H%M00.png") # type: ignore
        map_legend = f"{param.cbrtitle} ({param.unit})"
        
        try:
            if var == 'ww':
                "run plot for wave warning"
                tstart = timeinfo.strftime(f"%d %B %Y 07.00 WIB") # type: ignore
                tend = (timeinfo+forecast).strftime(f"%d %B %Y 07.00 WIB") # type: ignore
                map_title = timeinfo.strftime(f"{(param.figtitle).upper()}\n{tstart} - {tend}") # type: ignore
                self.__plot_wave_warning__(
                                          model,
                                          lat, 
                                          lon, 
                                          latlon_intv, 
                                          cmap,  # type: ignore
                                          lvl,  # type: ignore
                                          mag,  # type: ignore
                                          map_title, 
                                          map_area,
                                          map_legend, 
                                          file_name, 
                                          plot_shp, 
                                          shp, # type: ignore
                                          google,
                                          zoom4google,
                                          )
            else:
                map_title = timeinfo.strftime(f"{param.figtitle}\n%d %B %Y - %H UTC") # type: ignore
                self.__plot_spasial__(baserun,
                                      forecast,
                                      lat, 
                                      lon, 
                                      latlon_intv, 
                                      cmap,  # type: ignore
                                      lvl,  # type: ignore
                                      mag,  # type: ignore
                                      ucomp,  # type: ignore
                                      vcomp,  # type: ignore
                                      arw_intv, 
                                      arw_scale, 
                                      map_title, 
                                      map_area,
                                      map_legend, 
                                      file_name, 
                                      plot_shp, 
                                      shp, # type: ignore
                                      google,
                                      zoom4google,
                                      plotloc,
                                      liloc,
                                      )
            print(f"File tersimpan di {file_name}")
        except Exception as e:
            print(f"Error message: {e}")
            print(f"Error because: {type(e).__name__}")          # TypeError
            print(f"Error in file: {__file__}")                  # /tmp/example.py
            print(f"Error in line: {e.__traceback__.tb_lineno}")  # type: ignore # 2

    def plot_wave(
        self,
        ds:xr.Dataset,
        var:str,
        area:str,
        wilpel_name:str,
        out_dir:str,
        time=None,
        baserun=False,
        forecast=False,
        google: bool = False,
        zoom4google:int = 1,
        plotloc: bool = False,
        liloc: tuple[list[float], list[float], list[str]] = None,
    ):
        """Runner for Plotter 2D Wave"""
        if area == 'wilpel':
            wil_name = stamarCollection(wilpel_name)
            latlon_intv = wil_name.ledspace
            arw_intv = wil_name.arrowdensity
            arw_scale = wil_name.sv
            map_area = wil_name.title
            if wilpel_name == 'indonesia':
                plot_shp = False
                shp = None
            else:
                plot_shp = True
                shp = wil_name.shp
        elif area == 'wilpro':
            wil_name = wilproCollection(wilpel_name)
            latlon_intv = wil_name.ledspace
            arw_intv = wil_name.arrowdensity
            arw_scale = wil_name.sv
            plot_shp = True
            shp = wil_name.shp
            map_area = wil_name.title
        else:
            latlon_intv = 1
            arw_intv = 1
            arw_scale = 30
            plot_shp = False
            shp = None

        ds = ds.sel(lon=slice(wil_name.lonbounds[0], wil_name.lonbounds[1]), lat=slice(wil_name.latbounds[0], wil_name.latbounds[1])) # type: ignore
        
        lat = ds['lat'].data
        lon = ds['lon'].data

        param = mapCollection(var)
        lvl = param.clev
        # colormap = param.colorbar
        # try:
        #     cmap = LinearSegmentedColormap.from_list('custom_map', colormap)
        # except:
        #     cmap = colormap
        # norm = matplotlib.colors.BoundaryNorm(lvl, cmap.N)
        cmap = param.colorbar

        try:
            dirtitle = param.dirtitle
        except:
            dirtitle = None

        if var == 'ws':
            ucomp = ds[param.var1]
            vcomp = ds[param.var2]
            mag = np.sqrt(np.square(ucomp) + np.square(vcomp))
            ucomp, vcomp = 2*ucomp/mag, 2*vcomp/mag
        else:
            try:
                mag = ds[param.var1]
                dir = ds[param.var2]
                uhs = np.cos(np.deg2rad(dir))
                vhs = np.sin(np.deg2rad(dir))
                uvcomp = np.arctan2(vhs, uhs)
                ucomp = 2*np.cos(uvcomp)
                vcomp = 2*np.sin(uvcomp)
            except:
                mag = ds[param.var1]
                ucomp = None
                vcomp = None

        # if not area:
        #     ucomp, vcomp = 1.3*ucomp/2, 1.3*vcomp/2 # type: ignore
        
        try:
            timeinfo = pd.to_datetime(ds.time.data)
        except:
            timeinfo = time
        file_name = timeinfo.strftime(f"{out_dir}/{map_area.lower().replace(" - ", "_").replace(".", "").replace(" ", "_")}/{param.savename}_%Y%m%d%H.png") # type: ignore
        map_legend = f"{param.cbrtitle} ({param.unit})"
        
        try:
            map_title = f"{param.figtitle}\n{map_area}"
            self.__plot_spasial__(baserun=baserun,
                                    forecast=forecast,
                                    lat_data=lat, 
                                    lon_data=lon, 
                                    latlon_interval=latlon_intv, 
                                    color_map=cmap,  # type: ignore
                                    level=lvl,  # type: ignore
                                    magnitude=mag,  # type: ignore
                                    u_comp=ucomp,  # type: ignore
                                    v_comp=vcomp,  # type: ignore
                                    skip=arw_intv, 
                                    scale=arw_scale, 
                                    dirtitle=dirtitle,
                                    map_title=map_title, 
                                    legend=map_legend, 
                                    file_name=file_name, 
                                    plot_shapefile=plot_shp, 
                                    shp=shp, # type: ignore
                                    googleplot=google,
                                    zoom4google=zoom4google,
                                    plotloc=plotloc,
                                    liloc=liloc,
                                    )
            print(f"File saved at {file_name}")
        except Exception as e:
            print(f"Error message: {e}")
            print(f"Error because: {type(e).__name__}")          # TypeError
            print(f"Error in file: {__file__}")                  # /tmp/example.py
            print(f"Error in line: {e.__traceback__.tb_lineno}")  # type: ignore # 2
            print(f"Full error message: {traceback.format_exc()}")

    def plot_flow(
        self, 
        ds:xr.Dataset, 
        var:str, 
        area:str, 
        wilpel_name:str, 
        out_dir:str,
        time=None,
        baserun=datetime,
        forecast=datetime,
        depth=int,
        google: bool = False,
        zoom4google:int = 1,
        plotloc: bool = False,
        liloc: tuple[list[float], list[float], list[str]] = None,
    ):
        """Runner for Plotter 2D Flow"""
        if area == 'wilpel':
            wil_name = stamarCollection(wilpel_name)
            latlon_intv = wil_name.ledspace
            arw_intv = wil_name.arrowdensity
            arw_scale = wil_name.sv
            map_area = wil_name.title
            if wilpel_name == 'indonesia':
                plot_shp = False
                shp = None
            else:
                plot_shp = True
                shp = wil_name.shp
        elif area == 'wilpro':
            wil_name = wilproCollection(wilpel_name)
            latlon_intv = wil_name.ledspace
            arw_intv = wil_name.arrowdensity
            arw_scale = wil_name.sv
            plot_shp = True
            shp = wil_name.shp
            map_area = wil_name.title
        else:
            latlon_intv = 1
            arw_intv = 1
            arw_scale = 30
            plot_shp = False
            shp = None

        ds = ds.sel(lon=slice(wil_name.lonbounds[0], wil_name.lonbounds[1]), lat=slice(wil_name.latbounds[0], wil_name.latbounds[1])) # type: ignore
        
        lat = ds['lat'].data
        lon = ds['lon'].data

        param = mapCollection(var)
        lvl = param.clev
        # colormap = param.colorbar
        # try:
        #     cmap = LinearSegmentedColormap.from_list('custom_map', colormap)
        # except:
        #     cmap = colormap
        # norm = matplotlib.colors.BoundaryNorm(lvl, cmap.N)
        cmap = param.colorbar

        try:
            dirtitle = param.dirtitle
        except:
            dirtitle = None
    
        if var == 's' or var == 'st' or var == 'sl' or var == 'epv':
            ucomp = None
            vcomp = None
            mag = ds[param.var1]
        elif var == 'csd':
            ucomp = ds[param.var1]*100
            vcomp = ds[param.var2]*100
            mag = np.sqrt(np.square(ucomp) + np.square(vcomp))
            ucomp, vcomp = 2*ucomp/mag, 2*vcomp/mag

        if not area:
            ucomp, vcomp = 1.3*ucomp/2, 1.3*vcomp/2 # type: ignore
        
        try:
            timeinfo = pd.to_datetime(ds.time.data)
        except:
            timeinfo = time
        file_name = timeinfo.strftime(f"{out_dir}/{map_area.lower().replace(" - ", "_").replace(".", "").replace(" ", "_")}/{param.savename}_{depth}_%Y%m%d%H.png") # type: ignore
        map_legend = f"{param.cbrtitle} ({param.unit})"
        
        try:
            map_title = timeinfo.strftime(f"{param.figtitle}\n{map_area}") # type: ignore
            self.__plot_spasial__(baserun=baserun,
                                    forecast=forecast,
                                    lat_data=lat, 
                                    lon_data=lon, 
                                    latlon_interval=latlon_intv, 
                                    color_map=cmap,  # type: ignore
                                    level=lvl,  # type: ignore
                                    magnitude=mag,  # type: ignore
                                    u_comp=ucomp,  # type: ignore
                                    v_comp=vcomp,  # type: ignore
                                    skip=arw_intv, 
                                    scale=arw_scale, 
                                    dirtitle=dirtitle,
                                    map_title=map_title, 
                                    legend=map_legend, 
                                    file_name=file_name, 
                                    plot_shapefile=plot_shp, 
                                    shp=shp, # type: ignore
                                    googleplot=google,
                                    zoom4google=zoom4google,
                                    plotloc=plotloc,
                                    liloc=liloc,
                                    )
            print(f"File saved at {file_name}")
        except Exception as e:
            print(f"Error message: {e}")
            print(f"Error because: {type(e).__name__}")          # TypeError
            print(f"Error in file: {__file__}")                  # /tmp/example.py
            print(f"Error in line: {e.__traceback__.tb_lineno}")  # type: ignore # 2
            print(f"Full error message: {traceback.format_exc()}")

class mapCollection:
    """
    Collection of map variables for plotter
    
    Usage:
    metapicker(param:str)
    
    Example:
    metapicker('swh')
    """
    def __init__(self,mpick):
        mdict = {'swh' : {'color' : self.__cswh__,
                          'meta'  : self.__mswh__},
                 'ws'  : {'color' : self.__cws__,
                          'meta'  : self.__mws__},
                 'wg'  : {'color' : self.__cwg__,
                          'meta'  : self.__mwg__},
                 'mwh' : {'color' : self.__cswh__,
                          'meta'  : self.__mmwh__},
                 'wmp' : {'color' : self.__cwmp__,
                          'meta'  : self.__mwmp__},
                 'wml' : {'color' : self.__cwml__,
                          'meta'  : self.__mwml__},
                 'psh' : {'color' : self.__cswh__,
                          'meta'  : self.__mpsh__},
                 'psp' : {'color' : self.__cwmp__, #not ok
                          'meta'  : self.__mpsp__},
                 'wsh' : {'color' : self.__cswh__,
                          'meta'  : self.__mwsh__},
                 'wsp' : {'color' : self.__cwmp__, #not ok
                          'meta'  : self.__mwsp__},
                 'wpp' : {'color' : self.__cwpp__,
                          'meta'  : self.__mwpp__},
                 'wpl' : {'color' : self.__cwpl__,
                          'meta'  : self.__mwpl__},
                 'csd' : {'color' : self.__ccsd__,
                          'meta'  : self.__mcsd__},
                 's'   : {'color' : self.__cs__,
                          'meta'  : self.__ms__},
                 'st'  : {'color' : self.__cst__,
                          'meta'  : self.__mst__},
                 'sl'  : {'color' : self.__csl__,
                          'meta'  : self.__msl__},
                 'vv'  : {'color' : self.__cvv__,
                          'meta'  : self.__mvv__},
                 'ww'  : {'color' : self.__cww__,
                          'meta'  : self.__mww__}}
        
        mdict[mpick]['color']()
        mdict[mpick]['meta']()
    
    def __cswh__(self):
        self.clev = [0,0.5,0.75,1,1.25,1.5,2,2.5,3,3.5,4,5,6,7]
        self.extend = 'max'
        self.colorbar = ((0.0274509803921569,0.364705882352941,0.901960784313726),
                         (0.192156862745098,0.458823529411765,0.737254901960784),
                         (0.356862745098039,0.745098039215686,0.905882352941177),
                         (0.00392156862745098,0.984313725490196,0.737254901960784),
                         (0.00392156862745098,0.843137254901961,0.262745098039216),
                         (1,0.984313725490196,0.321568627450980),
                         (1,0.670588235294118,0.192156862745098),
                         (1,0.490196078431373,0.160784313725490),
                         (0.611764705882353,0.270588235294118,0.0627450980392157),
                         (0.905882352941177,0.270588235294118,0.227450980392157),
                         (0.780392156862745,0.172549019607843,0.196078431372549),
                         (0.905882352941177,0.203921568627451,0.776470588235294),
                         (0.709803921568628,0.203921568627451,0.607843137254902),
                         (0.411764705882353,0.113725490196078,0.466666666666667))
        
    def __cswhteluk__(self):
        self.clev = [0,0.125,0.25,0.375,0.5,0.625,0.75,0.875,1,1.125,1.25,1.375,1.5,1.625]
        self.extend = 'max'
        self.colorbar = ((0.0274509803921569,0.364705882352941,0.901960784313726),
                         (0.192156862745098,0.458823529411765,0.737254901960784),
                         (0.356862745098039,0.745098039215686,0.905882352941177),
                         (0.00392156862745098,0.984313725490196,0.737254901960784),
                         (0.00392156862745098,0.843137254901961,0.262745098039216),
                         (1,0.984313725490196,0.321568627450980),
                         (1,0.670588235294118,0.192156862745098),
                         (1,0.490196078431373,0.160784313725490),
                         (0.611764705882353,0.270588235294118,0.0627450980392157),
                         (0.905882352941177,0.270588235294118,0.227450980392157),
                         (0.780392156862745,0.172549019607843,0.196078431372549),
                         (0.905882352941177,0.203921568627451,0.776470588235294),
                         (0.709803921568628,0.203921568627451,0.607843137254902),
                         (0.411764705882353,0.113725490196078,0.466666666666667))
        
    def __cws__(self):
        self.clev = [0,2,4,6,8,10,15,20,25,30,35,40,50,60]
        self.extend = 'max'
        self.colorbar = ((0.776470588000000,0.921568627000000,1),
                         (0.647058824000000,0.843137255000000,0.905882353000000),
                         (0.388235294000000,0.780392157000000,0.968627451000000),
                         (0.709803922000000,1,0.741176471000000),
                         (0.223529412000000,0.890196078000000,0.419607843000000),
                         (0.709803922000000,0.874509804000000,0.450980392000000),
                         (0.937254902000000,0.858823529000000,0.419607843000000),
                         (0.968627451000000,0.729411765000000,0.450980392000000),
                         (1,0.364705882000000,0.129411765000000),
                         (0.807843137000000,0.125490196000000,0.0627450980000000),
                         (1,0.125490196000000,0.160784314000000),
                         (0.905882353000000,0.219607843000000,0.776470588000000),
                         (0.678431373000000,0.203921569000000,0.611764706000000),
                         (0.419607843000000,0.0941176470000000,0.482352941000000))

    def __cwg__(self):
        self.clev = [0,2,4,6,8,10,15,20,25,30,35,40,50,60]
        self.extend = 'max'
        self.colorbar = ((0.776470588000000,0.921568627000000,1),
                         (0.647058824000000,0.843137255000000,0.905882353000000),
                         (0.388235294000000,0.780392157000000,0.968627451000000),
                         (0.709803922000000,1,0.741176471000000),
                         (0.223529412000000,0.890196078000000,0.419607843000000),
                         (0.709803922000000,0.874509804000000,0.450980392000000),
                         (0.937254902000000,0.858823529000000,0.419607843000000),
                         (0.968627451000000,0.729411765000000,0.450980392000000),
                         (1,0.364705882000000,0.129411765000000),
                         (0.807843137000000,0.125490196000000,0.0627450980000000),
                         (1,0.125490196000000,0.160784314000000),
                         (0.905882353000000,0.219607843000000,0.776470588000000),
                         (0.678431373000000,0.203921569000000,0.611764706000000),
                         (0.419607843000000,0.0941176470000000,0.482352941000000))
        
    def __cwmp__(self):
        self.clev = [0,2,4,6,8,10,12,14,16,18,20,22,24]
        self.extend = 'max'
        self.colorbar = ((0,0.203921569000000,0.678431373000000),
                         (0,0.333333333000000,0.776470588000000),
                         (0,0.490196078000000,0.937254902000000),
                         (0,0.780392157000000,0.937254902000000),
                         (0.129411765000000,0.968627451000000,0.905882353000000),
                         (0.352941176000000,0.905882353000000,0.678431373000000),
                         (0.807843137000000,0.890196078000000,0.290196078000000),
                         (1,1,0),
                         (0.905882353000000,0.713725490000000,0.0313725490000000),
                         (0.905882353000000,0.364705882000000,0),
                         (0.870588235000000,0.109803922000000,0.0627450980000000),
                         (0.611764706000000,0.0313725490000000,0.0313725490000000),
                         (0.290196078000000,0,0))

    def __cwpp__(self):
        self.clev = [0,2,4,6,8,10,12,14,16,18,20,22,24]
        self.extend = 'max'
        self.colorbar = ((0,0.203921569000000,0.678431373000000),
                         (0,0.333333333000000,0.776470588000000),
                         (0,0.490196078000000,0.937254902000000),
                         (0,0.780392157000000,0.937254902000000),
                         (0.129411765000000,0.968627451000000,0.905882353000000),
                         (0.352941176000000,0.905882353000000,0.678431373000000),
                         (0.807843137000000,0.890196078000000,0.290196078000000),
                         (1,1,0),
                         (0.905882353000000,0.713725490000000,0.0313725490000000),
                         (0.905882353000000,0.364705882000000,0),
                         (0.870588235000000,0.109803922000000,0.0627450980000000),
                         (0.611764706000000,0.0313725490000000,0.0313725490000000),
                         (0.290196078000000,0,0))
        
    def __cwml__(self):
        self.clev = [0, 5, 10, 15, 25, 50, 75, 100, 125, 150, 200, 250, 300]
        self.extend = 'max'
        self.colorbar = ((0,0.203921569000000,0.678431373000000),
                         (0,0.333333333000000,0.776470588000000),
                         (0,0.490196078000000,0.937254902000000),
                         (0,0.780392157000000,0.937254902000000),
                         (0.129411765000000,0.968627451000000,0.905882353000000),
                         (0.352941176000000,0.905882353000000,0.678431373000000),
                         (0.807843137000000,0.890196078000000,0.290196078000000),
                         (1,1,0),
                         (0.905882353000000,0.713725490000000,0.0313725490000000),
                         (0.905882353000000,0.364705882000000,0),
                         (0.870588235000000,0.109803922000000,0.0627450980000000),
                         (0.611764706000000,0.0313725490000000,0.0313725490000000),
                         (0.290196078000000,0,0))
        
    def __cwpl__(self):
        self.clev = [0, 5, 10, 15, 25, 50, 75, 100, 125, 150, 200, 250, 300]
        self.extend = 'max'
        self.colorbar = ((0,0.203921569000000,0.678431373000000),
                         (0,0.333333333000000,0.776470588000000),
                         (0,0.490196078000000,0.937254902000000),
                         (0,0.780392157000000,0.937254902000000),
                         (0.129411765000000,0.968627451000000,0.905882353000000),
                         (0.352941176000000,0.905882353000000,0.678431373000000),
                         (0.807843137000000,0.890196078000000,0.290196078000000),
                         (1,1,0),
                         (0.905882353000000,0.713725490000000,0.0313725490000000),
                         (0.905882353000000,0.364705882000000,0),
                         (0.870588235000000,0.109803922000000,0.0627450980000000),
                         (0.611764706000000,0.0313725490000000,0.0313725490000000),
                         (0.290196078000000,0,0))
        
    def __ccsd__(self):
        self.clev = [0, 5, 10, 20, 30, 45, 60, 80, 100, 150, 200, 300, 400]
        self.extend = 'max'
        self.colorbar = ((0.0, 0.2980392156862745, 0.6),
                         (0.0, 0.5019607843137255, 1.0),
                         (0.4, 0.6980392156862745, 1.0),
                         (0.4, 1.0, 1.0),
                         (0.0, 0.9411764705882353, 0.5882352941176471),
                         (0.0, 0.8431372549019608, 0.0),
                         (0.6, 1.0, 0.043137254901960784),
                         (1.0, 1.0, 0.3137254901960784),
                         (1.0, 0.6, 0.3137254901960784),
                         (1.0, 0.5019607843137255, 0.0),
                         (0.8, 0.4, 0.0),
                         (0.8, 0.0, 0.0),
                         (0.6, 0.0, 0.0))
    
    def __cs__(self):
        self.clev = [30,30.5,31,31.5,32,32.5,33,33.5,34,34.5,35,35.5,36]
        self.extend = 'both'
        self.colorbar = ((0.184313725000000,0.235294118000000,0.549019608000000),
                         (0.231372549000000,0.317647059000000,0.627450980000000),
                         (0.247058824000000,0.364705882000000,0.670588235000000),
                         (0.254901961000000,0.470588235000000,0.725490196000000),
                         (0.156862745000000,0.698039216000000,0.917647059000000),
                         (0.384313725000000,0.788235294000000,0.803921569000000),
                         (0.450980392000000,0.768627451000000,0.623529412000000),
                         (0.623529412000000,0.800000000000000,0.368627451000000),
                         (0.870588235000000,0.886274510000000,0.254901961000000),
                         (0.972549020000000,0.749019608000000,0.168627451000000),
                         (0.929411765000000,0.533333333000000,0.184313725000000),
                         (0.929411765000000,0.270588235000000,0.215686275000000),
                         (0.878431373000000,0.180392157000000,0.180392157000000),
                         (0.568627451000000,0.149019608000000,0.156862745000000))
    
    def __cst__(self):
        # self.clev = [16,18,20,22,24,26,28,30,32,34,36]
        self.clev = [16,18,20,22,24,26,26.5,27,27.5,28,28.5,29,29.5,30,30.5,31,31.5,32,34,36]
        self.extend = 'both'
        self.colorbar = ((0.00392156900000000,0.00392156900000000,0.941176471000000),
                         (0.274509804000000,0.356862745000000,0.988235294000000),
                         (0.282352941000000,0.627450980000000,0.980392157000000),
                         (0.0627450980000000,0.901960784000000,0.972549020000000),
                         (0.184313725000000,0.992156863000000,0.760784314000000),
                         (0.537254902000000,0.992156863000000,0.450980392000000),
                         (0.831372549000000,1,0.156862745000000),
                         (0.949019608000000,0.831372549000000,0.00784313700000000),
                         (0.909803922000000,0.666666667000000,0),
                         (0.854901961000000,0.349019608000000,0),
                         (0.933333333333333,0.0666666666666667,0.0313725490196078),
                         (0.254901960784314,0.0470588235294118,0.0627450980392157))
    
    def __csl__(self):
        self.clev = [-2,-1.75,-1.5,-1.25,-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1,1.25,1.5,1.75,2]
        self.extend = 'both'
        # self.colorbar = matplotlib.colormaps['bwr']
        self.colorbar = ((0.0352941180000000,0.200000000000000,0.800000000000000),
                         (0.0352941180000000,0.200000000000000,0.800000000000000),
                         (0.203921569000000,0.203921569000000,1),
                         (0.356862745000000,0.356862745000000,1),
                         (0.407843137000000,0.407843137000000,1),
                         (0.509803922000000,0.509803922000000,1),
                         (0.611764706000000,0.611764706000000,1),
                         (0.819607843000000,0.819607843000000,1),
                         # (0.972549020000000,0.972549020000000,1),
                         # (0.972549020000000,0.972549020000000,1),
                         (1,0.870588235000000,0.870588235000000),
                         (1,0.768627451000000,0.768627451000000),
                         (1,0.611764706000000,0.611764706000000),
                         (1,0.509803922000000,0.509803922000000),
                         (1,0.407843137000000,0.403921569000000),
                         (1,0.305882353000000,0.305882353000000),
                         (1,0.203921569000000,0.203921569000000),
                         (0.956862745000000,0.125490196000000,0.0117647060000000)) 

    def __cvv__(self):
        self.clev = [-2,-1.75,-1.5,-1.25,-1,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1,1.25,1.5,1.75,2]
        self.extend = 'both'
        # self.colorbar = matplotlib.colormaps['bwr']
        self.colorbar = ((0.0352941180000000,0.200000000000000,0.800000000000000),
                         (0.0352941180000000,0.200000000000000,0.800000000000000),
                         (0.203921569000000,0.203921569000000,1),
                         (0.356862745000000,0.356862745000000,1),
                         (0.407843137000000,0.407843137000000,1),
                         (0.509803922000000,0.509803922000000,1),
                         (0.611764706000000,0.611764706000000,1),
                         (0.819607843000000,0.819607843000000,1),
                         # (0.972549020000000,0.972549020000000,1),
                         # (0.972549020000000,0.972549020000000,1),
                         (1,0.870588235000000,0.870588235000000),
                         (1,0.768627451000000,0.768627451000000),
                         (1,0.611764706000000,0.611764706000000),
                         (1,0.509803922000000,0.509803922000000),
                         (1,0.407843137000000,0.403921569000000),
                         (1,0.305882353000000,0.305882353000000),
                         (1,0.203921569000000,0.203921569000000),
                         (0.956862745000000,0.125490196000000,0.0117647060000000)) 

    def __cww__(self):
        self.clev = [0, 1.25, 2.5, 4, 6, 9]
        self.extend = ''
        self.colorbar = matplotlib.colors.ListedColormap(
                        [#"#0859E7", 
                         # "#3075BD", 
                         # "#63C3E7", 
                         # "#55FBBD", 
                         # "#48D342", ijo muda
                         '#FFFFFF',
                         "#FFFB52", 
                         # "#F9AD39", cokelat muda
                         "#F7792A", 
                         # "#A54518", dark choco
                         # "#E74941", red
                         "#CE2C38",
                         "red",
                         # "#EF37CE",  
                         "#B5349C"])
        
    def __mswh__(self):
        self.savename = 'swh'
        self.datatype = 'direction'
        self.mag      = 'hs'
        self.var1     = 'hs'
        self.var2     = 'dir'
        self.figtitle = 'Significant Wave Height and Direction'
        self.cbrtitle = 'Significant Wave Height'
        self.dirtitle = 'Wave Direction'
        self.unit     = 'm'
        self.nobathid = False
        
    def __mws__(self):
        self.savename = 'ws'
        self.datatype = 'vector'
        self.mag      = 'uwnd'
        self.var1     = 'uwnd'
        self.var2     = 'vwnd'
        self.figtitle = 'Wind Speed and Direction (10m)'
        self.cbrtitle = 'Wind Speed'
        self.dirtitle = 'Wind Direction'
        self.unit     = 'knot'
        self.nobathid = False

    def __mwg__(self):
        self.savename = 'wg'
        self.datatype = 'vector'
        self.mag      = 'gust'
        self.var1     = 'uwnd'
        self.var2     = 'vwnd'
        self.figtitle = 'Wind Gust Speed and Direction (10m)'
        self.cbrtitle = 'Wind Gust Speed'
        self.dirtitle = 'Wind Gust\nDirection'
        self.unit     = 'knot'
        self.nobathid = False

    def __mmwh__(self):
        self.savename = 'mwh'
        self.datatype = 'direction'
        self.mag      = 'hmax'
        self.var1     = 'hmax'
        self.var2     = 'dir'
        self.figtitle = 'Maximum Wave Height and Direction'
        self.cbrtitle = 'Maximum Wave Height'
        self.dirtitle = 'Wave Direction'
        self.unit     = 'm'
        self.nobathid = False
        
    def __mwmp__(self):
        self.savename = 'wmp'
        self.datatype = 'direction'
        self.mag      = 't01'
        self.var1     = 't01'
        self.var2     = 'dir'
        self.figtitle = 'Mean Wave Period and Direction'
        self.cbrtitle = 'Mean Wave Period'
        self.dirtitle = 'Wave Direction'
        self.unit     = 'second'
        self.nobathid = False

    def __mwpp__(self):
        self.savename = 'wmp'
        self.datatype = 'direction'
        self.mag      = 'wpp'
        self.var1     = 'wpp'
        self.var2     = 'dir'
        self.figtitle = 'Peak Wave Period and Direction'
        self.cbrtitle = 'Peak Wave Period'
        self.dirtitle = 'Wave Direction'
        self.unit     = 'second'
        self.nobathid = False

    def __mwml__(self):
        self.savename = 'wml'
        self.datatype = 'direction'
        self.mag      = 'lm'
        self.var1     = 'lm'
        self.var2     = 'dir'
        self.figtitle = 'Wave Mean Length and Direction'
        self.cbrtitle = 'Wave Mean Length'
        self.dirtitle = 'Wave Direction'
        self.unit     = 'meter'
        self.nobathid = False
        
    def __mwpl__(self):
        self.savename = 'wpl'
        self.datatype = 'direction'
        self.mag      = 'wpl'
        self.var1     = 'wpl'
        self.var2     = 'wpd'
        self.figtitle = 'Wave Peak Length and Direction'
        self.cbrtitle = 'Wave Peak Length'
        self.dirtitle = 'Wave Direction'
        self.unit     = 'meter'
        self.nobathid = False

    def __mpsh__(self):
        self.savename = 'psh'
        self.datatype = 'direction'
        self.mag      = 'phs01'
        self.var1     = 'phs01'
        self.var2     = 'pdi01'
        self.figtitle = 'Primary Swell Height and Direction'
        self.cbrtitle = 'Primary Swell Height'
        self.dirtitle = 'Primary Swell\nDirection'
        self.unit     = 'm'
        self.nobathid = True
        
    def __mpsp__(self):
        self.savename = 'psp'
        self.datatype = 'magnitude'
        self.mag      = 'ptp01'
        self.var1     = 'ptp01'
        self.var2     = 'pdi01'
        self.figtitle = 'Primary Swell Period and Direction'
        self.cbrtitle = 'Primary Swell Period'
        self.dirtitle = 'Primary Swell\nDirection'
        self.unit     = 'second'
        self.nobathid = True
        
    def __mwsh__(self):
        self.savename = 'wsh'
        self.datatype = 'direction'
        self.mag      = 'phs00'
        self.var1     = 'phs00'
        self.var2     = 'pdi00'
        self.figtitle = 'Wind Sea Height and Direction'
        self.cbrtitle = 'Wind Sea Height'
        self.dirtitle = 'Wind Sea\nDirection'
        self.unit     = 'm'
        self.nobathid = True
        
    def __mwsp__(self):
        self.savename = 'wsp'
        self.datatype = 'magnitude'
        self.mag      = 'ptp00'
        self.var1     = 'ptp00'
        self.var2     = 'pdi00'
        self.figtitle = 'Wind sea period and Direction'
        self.cbrtitle = 'Wind sea period'
        self.dirtitle = 'Wind Sea\nDirection'
        self.unit     = 'second'
        self.nobathid = True
        
    def __mcsd__(self):
        self.savename = 'csd'
        self.datatype = 'vector'
        self.mag      = 'u'
        self.var1     = 'u'
        self.var2     = 'v'
        self.figtitle = 'Current Speed and Direction'
        self.cbrtitle = 'Current Speed'
        self.dirtitle = 'Current Direction'
        self.unit     = 'cm/s'
        self.avt      = 'Average'
        self.nobathid = True
        
    def __ms__(self):
        self.savename = 's'
        self.datatype = 'magnitude'
        self.mag      = 'S'
        self.var1     = 'S'
        self.var2     = 'S'
        self.figtitle = 'Salinity'
        self.cbrtitle = 'Salinity'
        self.unit     = 'PSU'
        self.avt      = 'Average'
        self.nobathid = True
        
    def __mst__(self):
        self.savename = 'st'
        self.datatype = 'magnitude'
        self.mag      = 'T'
        self.var1     = 'T'
        self.var2     = 'T'
        self.figtitle = 'Sea Temperature'
        self.cbrtitle = 'Sea Temperature'
        self.unit     = '°C'
        self.avt      = 'Average'
        self.nobathid = True
        
    def __msl__(self):
        self.savename = 'sl'
        self.datatype = 'magnitude'
        self.mag      = 'zeta'
        self.var1     = 'zeta'
        self.var2     = 'zeta'
        self.figtitle = 'Sea Surface Height'
        self.cbrtitle = 'Sea Surface Height'
        self.unit     = 'm'
        self.nobathid = True

    def __mvv__(self):
        self.savename = 'w'
        self.datatype = 'magnitude'
        self.mag      = 'w'
        self.var1     = 'w'
        self.var2     = 'w'
        self.figtitle = 'Vertical Velocity'
        self.cbrtitle = 'Vertical Velocity'
        self.unit     = 'cm/s'
        self.nobathid = True

    def __mww__(self):
        self.savename = 'ww'
        self.datatype = 'magnitude'
        self.mag      = 'hs'
        self.var1     = 'hs'
        self.var2     = 'dir'
        self.figtitle = 'Informasi Tinggi Gelombang'
        self.cbrtitle = ''
        self.dirtitle = ''
        self.unit     = 'm'
        self.nobathid = False

class stamarCollection:
    """
    Collection of stamar / wilpel [old]
    
    Usage:
    stamarcollectionofs(area:str)
    
    Example:
    stamarcollectionofs('ambon')
    """
    def __init__(self,spick):
        sdict = {
                'indonesia' : self.indonesia,
                'asia_australia' : self.asia_australia,
                'ambon' : self.ambon,
                'balikpapan' : self.balikpapan,
                'batam' : self.batam,
                'belawan' : self.belawan,
                'jayapura' : self.jayapura,
                'cilacap' : self.cilacap,
                'denpasar' : self.denpasar,
                'kendari' : self.kendari,
                'kupang' : self.kupang,
                'lampung' : self.lampung,
                'paotere' : self.paotere,
                'bitung' : self.bitung,
                'merauke' : self.merauke,
                'pontianak' : self.pontianak,
                'tanjung_priok' : self.tanjung_priok,
                'semarang' : self.semarang,
                'sorong' : self.sorong,
                'surabaya' : self.surabaya,
                'padang' : self.padang,
                'ternate' : self.ternate,
                'serang' : self.serang
                }
        
        sdict[spick.lower()]()
         
    def indonesia(self):
        self.lonbounds = [90,145.]
        self.latbounds = [-15,15.]
        self.shp = ''
        self.title = 'Indonesia'
        self.sv = 17
        self.arrowdensity = 30
        self.ledspace = 5
        self.editujunglonlat = True
        self.lon0 = 90
        self.lat0 = -15
        
    def asia_australia(self):
        self.lonbounds = [70.,155.]
        self.latbounds = [-30.,30.]
        self.shp = ''
        self.title = 'Asia Australia'
        self.sv = 17
        self.arrowdensity = 70
        self.ledspace = 5
        self.editujunglonlat = False
        self.lon0 = None
        self.lat0 = None
        
    def ambon(self):
        self.lonbounds = [123.,137.]
        self.latbounds = [-11.,-1.]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/ambon'
        self.title = 'Ambon'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 124
        self.lat0 = -8
        
    def balikpapan(self):
        self.lonbounds = [113.,125.]
        self.latbounds = [-5.,5.]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/balikpapan'
        self.title = 'Balikpapan'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 114
        self.lat0 = -6
        
    def batam(self):
        self.lonbounds = [100.,107.]
        self.latbounds = [-3.,3.2]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/batam'
        self.title = 'Batam'
        self.sv = 17
        self.arrowdensity = 7
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -2
        
    def belawan(self):
        self.lonbounds = [90,105.01]
        self.latbounds = [-3,9.01]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/belawan'
        self.title = 'Belawan'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 3
        self.editujunglonlat = True
        self.lon0 = 90
        self.lat0 = -3
        
    def jayapura(self):
        self.lonbounds = [130.,145.]
        self.latbounds = [-6.,7.]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/jayapura'
        self.title = 'Jayapura'
        self.sv = 13
        self.arrowdensity = 10
        self.ledspace = 4
        self.editujunglonlat = False
        self.lon0 = 132
        self.lat0 = -4

    def cilacap(self):
        self.lonbounds = [105.5,112.25]
        self.latbounds = [-12.,-7.]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/cilacap'
        self.title = 'Cilacap'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 1.5
        self.editujunglonlat = False
        self.lon0 = 107.5
        self.lat0 = -11
        
    def denpasar(self):
        self.lonbounds = [112.5,122.5]
        self.latbounds = [-14.,-4.5]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/denpasar'
        self.title = 'Denpasar'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 113
        self.lat0 = -13
        
    def kendari(self):
        self.lonbounds = [119.,129.]
        self.latbounds = [-8.5,0.5]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/kendari'
        self.title = 'Kendari'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 120
        self.lat0 = -8
          
    def kupang(self):
        self.lonbounds = [117.5,128.5]
        self.latbounds = [-14.75,-6.75]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/kupang'
        self.title = 'Kupang'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 118
        self.lat0 = -14
        
    def lampung(self):
        self.lonbounds = [97.,107.5]
        self.latbounds = [-9.05,-0.95]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/lampung'
        self.title = 'Lampung'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 98
        self.lat0 = -10
         
    def paotere(self):
        self.lonbounds = [115.,127.]
        self.latbounds = [-10.,-1.]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/paotere'
        self.title = 'Paotere'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 117
        self.lat0 = -9
        
    def bitung(self):
        self.lonbounds = [116.,129.5]
        self.latbounds = [-3.25,7.25]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/bitung'
        self.title = 'Bitung'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 4
        self.editujunglonlat = False
        self.lon0 = 116
        self.lat0 = 0
        
    def merauke(self):
        self.lonbounds = [130.,145.]
        self.latbounds = [-12.1,0.1]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/merauke'
        self.title = 'Merauke'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 4
        self.editujunglonlat = False
        self.lon0 = 132
        self.lat0 = -12
        
    def pontianak(self):
        self.lonbounds = [101.5,113.5]
        self.latbounds = [-4.6,7.6]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/pontianak'
        self.title = 'Pontianak'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 2.5
        self.editujunglonlat = False
        self.lon0 = 102.5
        self.lat0 = -2.5
        
    def tanjung_priok(self):
        self.lonbounds = [100.,113.]
        self.latbounds = [-12.,1.]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/tanjung_priok'
        self.title = 'Tanjung Priok'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9
        
    def semarang(self):
        self.lonbounds = [107.5,116.5]
        self.latbounds = [-9.,-1.]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/semarang'
        self.title = 'Semarang'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 108
        self.lat0 = -8
        
    def sorong(self):
        self.lonbounds = [125.5,138.5]
        self.latbounds = [-7.,7.]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/sorong'
        self.title = 'Sorong'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 4
        self.editujunglonlat = False
        self.lon0 = 128
        self.lat0 = -4
        
    def surabaya(self):
        self.lonbounds = [109.5,119.5]
        self.latbounds = [-13.5,-3.]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/surabaya'
        self.title = 'Surabaya'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 110
        self.lat0 = -13
        
    def padang(self):
        self.lonbounds = [94.,104.]
        self.latbounds = [-9.5,1.]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/padang'
        self.title = 'Padang'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 94
        self.lat0 = -6
        
    def ternate(self):
        self.lonbounds = [122.25,133.75]
        self.latbounds = [-3.25,7.5]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/ternate'
        self.title = 'Ternate'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 4
        self.editujunglonlat = False
        self.lon0 = 124
        self.lat0 = 0
                
    def serang(self):
        self.lonbounds = [100.,108.05]
        self.latbounds = [-11.,-2.95]
        self.shp = '/scratch/bmkg_4/Production_Unit/shp2019/serang'
        self.title = 'Serang'
        self.sv = 17
        self.arrowdensity = 10
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

class wilproCollection:
    """
    Collection of Wilpro for Plotter [new]
    
    Usage:
    wilproCollection(area:str)
    
    Example:
    wilproCollection('ambon')
    """
    def __init__(self,spick):
        self.shp = '/home/dev-001/data/shp/metoswilpro/METOS_WILPRO_20231018'
        self.gdf_plot = gpd.read_file(f'{self.shp}.shp')
        sdict = {
                'indonesia' : self.indonesia,
                'asia_australia' : self.asia_australia,
                'aceh' : self.aceh,
                'babel' : self.babel,
                'bali' : self.bali,
                'banten' : self.banten,
                'bengkulu' : self.bengkulu,
                'diy' : self.diy,
                'dki_jabar' : self.dki_jabar,
                'gorontalo' : self.gorontalo,
                'jambi' : self.jambi,
                'jateng' : self.jateng,
                'jatim' : self.jatim,
                'kalbar' : self.kalbar,
                'kalsel' : self.kalsel,
                'kaltara' : self.kaltara,
                'kalteng' : self.kalteng,
                'kaltim' : self.kaltim,
                'kep_riau' : self.kep_riau,
                'lampung' : self.lampung,
                'maluku' : self.maluku,
                'maluku_utara' : self.maluku_utara,
                'ntb' : self.ntb,
                'ntt' : self.ntt,
                'papua' : self.papua,
                'papua_barat': self.papua_barat,
                'papua_barat_daya': self.papua_barat_daya,
                'papua_selatan': self.papua_selatan,
                'papua_tengah': self.papua_tengah,
                'riau': self.riau,
                'sulbar': self.sulbar,
                'sulsel': self.sulsel,
                'sulteng': self.sulteng,
                'sultra': self.sultra,
                'sulut': self.sulut,
                'sumbar': self.sumbar,
                'sumut': self.sumut,
                'sumsel': self.sumsel
                }
        
        sdict[spick.lower()]()
         
    def indonesia(self):
        self.title = 'Indonesia'
        self.shp = self.gdf_plot[~self.gdf_plot['Met_Area'].isnull()].boundary
        self.lonbounds = [90,145.]
        self.latbounds = [-15,15.]
        self.sv = 21
        self.arrowdensity = 15
        self.ledspace = 5
        self.editujunglonlat = True
        self.lon0 = 90
        self.lat0 = -15
    
    def asia_australia(self):
        self.lonbounds = [70.,155.]
        self.latbounds = [-30.,30.]
        self.shp = ''
        self.title = 'Asia Australia'
        self.sv = 12
        self.arrowdensity = 70
        self.ledspace = 5
        self.editujunglonlat = False
        self.lon0 = None
        self.lat0 = None
        
    def aceh(self):
        self.title = 'Aceh'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1, self.total_bounds[2]+1]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 16
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 124
        self.lat0 = -8
        
    def babel(self):
        self.title = 'Kep. Bangka Belitung'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1, self.total_bounds[2]+1]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 16
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 124
        self.lat0 = -8
        
    def bali(self):
        self.title = 'Bali'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.3, self.total_bounds[2]+0.3]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 1
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 114
        self.lat0 = -6
        
    def banten(self):
        self.title = 'Banten'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.2, self.total_bounds[2]+0.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 1
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -2
        
    def bengkulu(self):
        self.title = 'Bengkulu'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.5, self.total_bounds[2]+0.5]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 18
        self.arrowdensity = 1
        self.ledspace = 3
        self.editujunglonlat = True
        self.lon0 = 90
        self.lat0 = -3
        
    def diy(self):
        self.title = 'DI Yogyakarta'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.7, self.total_bounds[2]+0.7]
        self.latbounds = [self.total_bounds[1]-0.7, self.total_bounds[3]+0.5]   
        self.sv = 14
        self.arrowdensity = 1
        self.ledspace = 4
        self.editujunglonlat = False
        self.lon0 = 132
        self.lat0 = -4

    def dki_jabar(self):
        self.title = 'DKI Jakarta - Jawa Barat'
        self.title1 = 'DKI Jakarta'
        self.title2 = 'Jawa Barat'
        self.shp = self.gdf_plot[(self.gdf_plot['Perairan'] == f"{self.title1}") | (self.gdf_plot['Perairan'] == f"{self.title2}")].boundary        
        self.total_bounds = self.gdf_plot[(self.gdf_plot['Perairan'] == f"{self.title1}") | (self.gdf_plot['Perairan'] == f"{self.title2}")]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1.2, self.total_bounds[2]+1.2]
        self.latbounds = [self.total_bounds[1]-0.4, self.total_bounds[3]+0.4]   
        self.sv = 14
        self.arrowdensity = 2
        self.ledspace = 1.5
        self.editujunglonlat = False
        self.lon0 = 107.5
        self.lat0 = -11
        
    def gorontalo(self):
        self.title = 'Gorontalo'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.2, self.total_bounds[2]+0.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 1
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 113
        self.lat0 = -13
        
    def jambi(self):
        self.title = 'Jambi'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.3, self.total_bounds[2]+0.3]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 1
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 120
        self.lat0 = -8
          
    def jateng(self):
        self.title = 'Jawa Tengah'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.6, self.total_bounds[2]+0.6]
        self.latbounds = [self.total_bounds[1]-0.4, self.total_bounds[3]+0.4]   
        self.sv = 14
        self.arrowdensity = 2
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 118
        self.lat0 = -14
        
    def jatim(self):
        self.title = 'Jawa Timur'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.2, self.total_bounds[2]+0.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 15
        self.arrowdensity = 2
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 98
        self.lat0 = -10
         
    def kalbar(self):
        self.title = 'Kalimantan Barat'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1.8, self.total_bounds[2]+1.8]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 16
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 117
        self.lat0 = -9
        
    def kalsel(self):
        self.title = 'Kalimantan Selatan'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.2, self.total_bounds[2]+0.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 16
        self.arrowdensity = 1
        self.ledspace = 4
        self.editujunglonlat = False
        self.lon0 = 116
        self.lat0 = 0
        
    def kaltara(self):
        self.title = 'Kalimantan Utara'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1, self.total_bounds[2]+1]
        self.latbounds = [self.total_bounds[1]-0.3, self.total_bounds[3]+0.3]   
        self.sv = 14
        self.arrowdensity = 2
        self.ledspace = 4
        self.editujunglonlat = False
        self.lon0 = 132
        self.lat0 = -12
        
    def kalteng(self):
        self.title = 'Kalimantan Tengah'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1, self.total_bounds[2]+1]
        self.latbounds = [self.total_bounds[1]-0.8, self.total_bounds[3]+0.5]   
        self.sv = 14
        self.arrowdensity = 2
        self.ledspace = 2.5
        self.editujunglonlat = False
        self.lon0 = 102.5
        self.lat0 = -2.5
        
    def kaltim(self):
        self.title = 'Kalimantan Timur'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1.2, self.total_bounds[2]+1.4]
        self.latbounds = [self.total_bounds[1]-0.4, self.total_bounds[3]+0.4]   
        self.sv = 16
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9
        
    def kep_riau(self):
        self.title = 'Kep. Riau'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.3, self.total_bounds[2]+0.3]
        self.latbounds = [self.total_bounds[1]-0.3, self.total_bounds[3]+0.3]   
        self.sv = 14
        self.arrowdensity = 3
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 108
        self.lat0 = -8
        
    def lampung(self):
        self.title = 'Lampung'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.2, self.total_bounds[2]+0.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 17
        self.arrowdensity = 1
        self.ledspace = 4
        self.editujunglonlat = False
        self.lon0 = 128
        self.lat0 = -4
        
    def maluku(self):
        self.title = 'Maluku'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.2, self.total_bounds[2]+0.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 17
        self.arrowdensity = 3
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 110
        self.lat0 = -13
        
    def maluku_utara(self):
        self.title = 'Maluku Utara'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.2, self.total_bounds[2]+0.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 15
        self.arrowdensity = 2
        self.ledspace = 2
        self.editujunglonlat = False
        self.lon0 = 94
        self.lat0 = -6
        
    def ntb(self):
        self.title = 'Nusa Tenggara Barat'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.5, self.total_bounds[2]+0.5]
        self.latbounds = [self.total_bounds[1]-0.5, self.total_bounds[3]+0.5]   
        self.sv = 16
        self.arrowdensity = 2
        self.ledspace = 4
        self.editujunglonlat = False
        self.lon0 = 124
        self.lat0 = 0
                
    def ntt(self):
        self.title = 'Nusa Tenggara Timur'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.5, self.total_bounds[2]+0.5]
        self.latbounds = [self.total_bounds[1]-0.5, self.total_bounds[3]+0.5]   
        self.sv = 17
        self.arrowdensity = 3
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def papua(self):
        self.title = 'Papua'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.7, self.total_bounds[2]+0.7]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 3
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def papua_barat(self):
        self.title = 'Papua Barat'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.7, self.total_bounds[2]+0.7]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def papua_barat_daya(self):
        self.title = 'Papua Barat Daya'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.2, self.total_bounds[2]+0.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 3
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def papua_selatan(self):
        self.title = 'Papua Selatan'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.5, self.total_bounds[2]+0.5]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 16
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def papua_tengah(self):
        self.title = 'Papua Tengah'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.4, self.total_bounds[2]+0.4]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def riau(self):
        self.title = 'Riau'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.6, self.total_bounds[2]+0.6]
        self.latbounds = [self.total_bounds[1]-0.4, self.total_bounds[3]+0.4]   
        self.sv = 16
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def sulbar(self):
        self.title = 'Sulawesi Barat'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1.2, self.total_bounds[2]+1.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def sulsel(self):
        self.title = 'Sulawesi Selatan'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1.2, self.total_bounds[2]+1.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 16
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def sulteng(self):
        self.title = 'Sulawesi Tengah'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.5, self.total_bounds[2]+0.5]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def sultra(self):
        self.title = 'Sulawesi Tenggara'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-0.2, self.total_bounds[2]+0.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 16
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def sulut(self):
        self.title = 'Sulawesi Utara'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1.2, self.total_bounds[2]+1.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 3
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def sumbar(self):
        self.title = 'Sumatra Barat'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1.2, self.total_bounds[2]+1.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 16
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def sumut(self):
        self.title = 'Sumatra Utara'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1.2, self.total_bounds[2]+1.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 16
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

    def sumsel(self):
        self.title = 'Sumatra Selatan'
        self.shp = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"].boundary        
        self.total_bounds = self.gdf_plot[self.gdf_plot['Perairan'] == f"{self.title}"]['geometry'].total_bounds
        self.lonbounds = [self.total_bounds[0]-1.2, self.total_bounds[2]+1.2]
        self.latbounds = [self.total_bounds[1]-0.2, self.total_bounds[3]+0.2]   
        self.sv = 14
        self.arrowdensity = 2
        self.ledspace = 3
        self.editujunglonlat = False
        self.lon0 = 102
        self.lat0 = -9

wilpelist = [
    'indonesia',
    'asia_australia',
    'ambon',
    'balikpapan',
    'batam',
    'belawan',
    'jayapura',
    'cilacap',
    'denpasar',
    'kendari',
    'kupang',
    'lampung',
    'paotere',
    'bitung',
    'merauke',
    'pontianak',
    'tanjung_priok',
    'semarang',
    'sorong',
    'surabaya',
    'padang',
    'ternate',
    'serang'
]

wilprolist = [
    'indonesia',
     'aceh',
     'babel',
     'bali',
     'banten',
     'bengkulu',
     'diy',
     'dki_jabar',
     'gorontalo',
     'jambi',
     'jateng',
     'jatim',
     'kalbar',
     'kalsel',
     'kaltara',
     'kalteng',
     'kaltim',
     'kep_riau',
     'lampung',
     'maluku',
     'maluku_utara',
     'ntb',
     'ntt',
     'papua',
     'papua_barat',
     'papua_barat_daya',
     'papua_selatan',
     'papua_tengah',
     'riau',
     'sulbar',
     'sulsel',
     'sulteng',
     'sultra',
     'sulut',
     'sumbar',
     'sumut',
     'sumsel'
]
