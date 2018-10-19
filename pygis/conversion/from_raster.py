"""
@author   Chris R. Vernon
@email:   chris.vernon@pnnl.gov
@Project: pygis
License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2017, Battelle Memorial Institute
"""

import gdal
import numpy as np


def raster_to_array(f, band=1):
    """
    Read a raster file to a numpy array.

    :param f:        Full path with filename and extension to the input raster
    :param band:     Raster band number
    :return:         numpy array, no data value
    """
    r = gdal.Open(f)
    band = r.GetRasterBand(band)

    return np.array(band.ReadAsArray()), band.GetNoDataValue()