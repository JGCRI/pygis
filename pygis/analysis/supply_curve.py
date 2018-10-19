"""
@author   Chris R. Vernon
@email:   chris.vernon@pnnl.gov
@Project: pygis
License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2017, Battelle Memorial Institute
"""

import os
import numpy as np
import pandas as pd
import seaborn as sns

# no interactive display for use with HPC
import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt

import pygis.analysis.reclass as rcl
import pygis.conversion.from_raster as cnv


def test_shape_match(arr_1, arr_2):
    """
    Test to make sure the shape of two arrays are equal.

    :param arr_1:           Numpy array
    :param arr_2:           Numpy array
    """
    s_a1 = arr_1.shape
    s_a2 = arr_2.shape

    if s_a1 != s_a2:
        raise ValueError(
            "USAGE:  Raster resolutions do not match.  Raster_1 shape: {}, Raster_2 shape: {}".format(s_a1, s_a2))


def supply_curve(xfile, yfile, y_label='price', x_label='energy', n_bins=False,
                 bin_list=False, reclass_file=False, mask_file=False, mask_value=None,
                 out_file=False, out_plot=False):
    """
    Build supply curve data and plot from two input rasters assigned to each axis.

    :param xfile:         Full path with file name and extension to the input raster for the x-axis
    :param yfile:         Full path with file name and extension to the input raster for the y-axis
    :param y_label:       Name for the y-axis
    :param x_label:       Name for the x-axis
    :param n_bins:        If choosing to create bins dynamically, specify an integer number of bins.
                          This will create an equal interval binning based on the non-nodata minimum and
                          maximum range.
    :param bin_list:      This is another option for providing bin designation as a list of lists.
                          Either a list of lists containing [[old_value, new_value], [...]]
                          or a list of list containing [[start_value, to_value, new_value], [...]],
                          where start_value is <= to old value, to_value is > old value.
    :param reclass_file:  This is another option for providing bin designation as a CSV with headers. Use
                          start_value, to_value, new_value format.
    :param mask_file:     Optional, full path with file name and extension to the input raster mask file.
                          Only elements within the specific zone will be accounted for.
    :param mask_value:    If using a mask file, specifiy the mask value to use.
    :param out_file:      Optionally export the supply curve data as a CSV.
    :param out_plot:      Optionally export the supply curve as a plot.
    """

    # read rasters for x and y axis to arrays and get nodata values
    x_arr, x_nodata = cnv.raster_to_array(xfile)
    y_arr, y_nodata = cnv.raster_to_array(yfile)

    # test for shape match
    test_shape_match(x_arr, y_arr)

    # if mask file provided
    if mask_file:

        if mask_value is None:
            raise ValueError("USAGE:  Please specify a 'mask_value' when using a mask file.")

        m_arr, m_nodata = cnv.raster_to_array(mask_file)

        # test shape
        test_shape_match(m_arr, y_arr)

        # mask zone
        m_arr = np.where(m_arr == mask_value, True, False)
        x_arr = x_arr[m_arr]
        y_arr = y_arr[m_arr]

    # replace nodata value with 0
    if x_nodata:
        x_arr = np.where(x_arr == x_nodata, 0, x_arr)

    if y_nodata:
        y_arr = np.where(y_arr == y_nodata, 0, y_arr)

    # if reclass file provided
    if reclass_file:
        bin_list = pd.read_csv(reclass_file).values.tolist()

    # if a list of lists are passed
    elif bin_list:
        pass

    # if user wants to create equal interval bins providing the number of bins desired
    elif n_bins:
        bin_list = rcl.create_equal_interval_bins(y_arr, n_bins)

    else:
        raise ValueError("Please choose a binning option and retry.")

    # reclassify the y axis array
    y_arr = rcl.reclassify(y_arr, bin_list)
    y_bins = [i[-1] for i in bin_list]
    y_bins.sort()

    # get sum of target raster per bin
    x = np.bincount(np.searchsorted(y_bins, y_arr.flatten()), x_arr.flatten())

    # build output data frame with cumulative sum for x-axis values
    df = pd.DataFrame({y_label: y_bins, x_label: x})
    df.set_index(y_label, inplace=True)
    df = df.cumsum()
    df.reset_index(inplace=True)

    # add in bin information to data frame
    dfx = pd.DataFrame(bin_list, columns=['start_value', 'to_value', 'bin'])
    df[['start_value', 'to_value', 'bin']] = dfx

    # change y_label data from bin to start_value
    df[y_label] = df['start_value']

    if out_file:
        df.to_csv(out_file, index=False)

    if out_plot:
        sns.set()
        ax = df.plot(x=x_label, y=y_label, legend=False)
        ax.set_ylabel(y_label)
        plt.savefig(out_plot)

    return df


if __name__ == '__main__':

    root = '/pic/projects/GCAM/geospatial/data'

    f_cost = os.path.join(root, 'rast', 'COEwind.asc')
    f_energy = os.path.join(root, 'rast', 'TechPotWind.asc')
    f_regions = os.path.join(root, 'raster', 'reg32_0p5deg.tif')
    out_csv = os.path.join(root, 'outputs', 'COEwind_TechPotWind_supply_curve.csv')
    out_plot = os.path.join(root, 'outputs', 'COEwind_TechPotWind_supply_curve.png')

    df = supply_curve(f_energy, f_cost, x_label='Energy_kwh', y_label='Price',
                      n_bins=100000, mask_file=f_regions, mask_value=[1],
                      out_file=out_csv, out_plot=out_plot)
