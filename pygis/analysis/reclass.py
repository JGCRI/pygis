"""
@author   Chris R. Vernon
@email:   chris.vernon@pnnl.gov
@Project: pygis
License:  BSD 2-Clause, see LICENSE and DISCLAIMER files
Copyright (c) 2017, Battelle Memorial Institute
"""


import numpy as np


def create_equal_interval_bins(arr, n_bins=1):
    """
    Create an array of equal interval bins as a list of lists in the format of
    [[start_value, to_value, new_value], [...]]

    :param arr:               A 1D numpy array
    :param n_bins:            The number of bins to create
    :return:                  A list of lists
    """
    a_min = np.nanmin(arr)
    a_max = np.nanmax(arr)
    a_rng = a_max - a_min

    a_equal = a_rng / n_bins

    a_iter = np.arange(a_min, a_max + a_equal, a_equal)

    return [[i, a_iter[idx + 1], idx] for idx, i in enumerate(a_iter) if idx + 1 < len(a_iter)]


def reclassify(arr, reclass_list):
    """
    Reclassify numpy array using key value pair in dictionary.

    :param arr:             Numpy array
    :param reclass_list:    Either a list of lists containing [[old_value, new_value], [...]]
                            or a list of list containing [[start_value, to_value, new_value], [...]],
                            where start_value is <= to old value, to_value is > old value.
    """
    l_lst = len(reclass_list)

    for idx, k in enumerate(reclass_list):

        if len(k) == 3:

            if idx + 1 == l_lst:
                arr = np.where((arr >= k[0]) & (arr <= k[1]), k[2], arr)

            else:
                arr = np.where((arr >= k[0]) & (arr < k[1]), k[2], arr)

        else:
            arr = np.where(arr == k[0], k[1], arr)

    return arr