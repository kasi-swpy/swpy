import numpy as np


def rescale(data, imin, imax, omin, omax):
    return omin + (omax - omin) * (data - imin) / (imax - imin)


def byte_scale(data, imin=None, imax=None):
    if not imin:
        imin = np.min(data)
    if not imax:
        imax = np.max(data)
    data = rescale(data, imin, imax, omin=0, omax=255)
    return data.astype(np.uint8)
