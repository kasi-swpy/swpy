import textwrap
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from swpy.swds.dataset.utilities import BaseDataset
from swpy.swds.dataset.utilities import byte_scale
from swpy.swds.dataset.utilities import All, fits_header_to_Header


def sdo_open(filepath):
    hdu = fits.open(filepath)[-1]
    TELESCOP = hdu.header["TELESCOP"]
    if TELESCOP == "SDO/AIA" :
        dataset = AIADataset(filepath)
    elif TELESCOP == "SDO/HMI" :
        CONTENT = hdu.header["CONTENT"]
        if CONTENT == "MAGNETOGRAM" :
            dataset = HMIMagnetogramDataset(filepath)
        elif CONTENT == "CONTINUUM INTENSITY" :
            dataset = HMIContinuumDataset(filepath)
        elif CONTENT == "DOPPLERGRAM" :
            dataset = HMIDopplergramDataset(filepath)
        else :
            raise NameError("Unknown HMI content")
    else :
        raise NameError("Unknown SDO telescope")
    return dataset


class SDODataset(BaseDataset):
    def __init__(self, filepath, num_ext=None):
        super(SDODataset, self).__init__(filepath)
        if num_ext is None :
            num_ext = -1
        self.num_ext = num_ext
        self.all = fits.open(filepath)
        self.hdu = fits.open(filepath)[num_ext]

        self.parsing_header()
        self.parsing_data()

        self.institute = "NASA"
        self.satellite = "SDO"
        self.observatory = "SDO"


    def parsing_header(self):
        header = fits_header_to_Header(self.hdu.header)
        self.date = header["DATE-OBS"]        
        self.header = header

    def parsing_data(self):
        data = self.hdu.data
        self.dimension = data.shape
        self.data_num = data.size
        self.data = data

    def __repr__(self):
        rep = textwrap.dedent(f"""\
            -----------------------------------
            {self.header['TELESCOP']} {self.object} {self.header['T_REC']}
            header:\t\t dict
            data:\t\t np.ndarray
            all:\t\t astropy.io.fits.hdu.hdulist.HDUList
            -----------------------------------
            """)
        return rep


class AIADataset(SDODataset):
    def __init__(self, filepath):
        super(AIADataset, self).__init__(filepath)
        self.instrument = "AIA"
        self.telescope = "AIA"
        self.object = self.header["WAVE_STR"]

    def calibrate(self):
        """
        
        
        """
        pass


    def plot(self, vmin=None, vmax=None):
        exptime = self.header["EXPTIME"]
        wavelnth = self.header["WAVELNTH"]
        telescop = self.header["TELESCOP"]
        naxis1 = self.header["NAXIS1"]
        cdelt1 = self.header["CDELT1"]
        naxis2 = self.header["NAXIS2"]
        cdelt2 = self.header["CDELT2"]
        cunit1 = self.header["CUNIT1"]
        cunit2 = self.header["CUNIT2"]
        t_rec = self.header["T_REC"]
        pixlunit = self.header["PIXLUNIT"]

        data = self.data.copy() / exptime

        pixlunit = f"{pixlunit}/sec"

        xmin = - naxis1 / 2. * cdelt1
        xmax = naxis1 / 2. * cdelt1
        ymin = - naxis2 / 2. * cdelt2
        ymax = naxis2 / 2. * cdelt2

        if vmin is None :
            if wavelnth == 94:
                vmin = 1.5
            elif wavelnth == 131:
                vmin = 7.0
            elif wavelnth == 171:
                vmin = 10.
            elif wavelnth == 193:
                vmin = 120.
            elif wavelnth == 211:
                vmin = 30.
            elif wavelnth == 304:
                vmin = 15.
            elif wavelnth == 335:
                vmin = 3.5
            elif wavelnth == 1600:
                vmin = 0.
            elif wavelnth == 1700:
                vmin = 0.
            elif wavelnth == 4500:
                vmin = 0.
        
        if vmax is None :
            if wavelnth == 94:
                vmax = 50.
            elif wavelnth == 131:
                vmax = 1200.
            elif wavelnth == 171:
                vmax = 6000.
            elif wavelnth == 193:
                vmax = 6000.
            elif wavelnth == 211:
                vmax = 13000.
            elif wavelnth == 304:
                vmax = 600.
            elif wavelnth == 335:
                vmax = 1000.
            elif wavelnth == 1600:
                vmax = 1000.
            elif wavelnth == 1700:
                vmax = 2500.
            elif wavelnth == 4500:
                vmax = 26000.

        if wavelnth == 94:
            factor = 4.99803
        elif wavelnth == 131:
            factor = 6.99685
        elif wavelnth == 171:
            factor = 4.99803
        elif wavelnth == 193:
            factor = 2.99950
        elif wavelnth == 211:
            factor = 4.99801
        elif wavelnth == 304:
            factor = 4.99941
        elif wavelnth == 335:
            factor = 6.99734
        elif wavelnth == 1600:
            factor = 2.99911
        elif wavelnth == 1700:
            factor = 1.00026
        elif wavelnth == 4500:
            factor = 1.00026

        if wavelnth in [94, 171] :
            data = np.sqrt((data*factor).clip(vmin, vmax))
            vmin = np.sqrt(vmin)
            vmax = np.sqrt(vmax)
        elif wavelnth in [131, 193, 211, 304, 335] :
            data = np.log10((data*factor).clip(vmin, vmax))
            vmin = np.log10(vmin)
            vmax = np.log10(vmax)
        elif wavelnth in [1600, 1700, 4500] :
            data = (data*factor).clip(vmin, vmax)

        data = byte_scale(data, vmin, vmax)

        plt.figure()
        plt.imshow(data, extent = [xmin, xmax, ymin, ymax], cmap="gray")
        plt.title(f"{telescop} {wavelnth} {t_rec}")
        plt.xlabel(cunit1)
        plt.ylabel(cunit2)
        plt.colorbar(label=pixlunit)
        plt.show()


class HMIDataset(SDODataset):
    def __init__(self, filepath):
        super(HMIDataset, self).__init__(filepath)
        self.instrument = "HMI"
        self.telescope = "HMI"
        self.object = self.header["CONTENT"]

    def remove_nan(self):
        self.data[np.isnan(self.data)] = 0

    def plot(self, vmin=None, vmax=None):
        telescop = self.header["TELESCOP"]
        content = self.header["CONTENT"]
        naxis1 = self.header["NAXIS1"]
        cdelt1 = self.header["CDELT1"]
        naxis2 = self.header["NAXIS2"]
        cdelt2 = self.header["CDELT2"]
        cunit1 = self.header["CUNIT1"]
        cunit2 = self.header["CUNIT2"]
        t_rec = self.header["T_REC"]
        bunit = self.header["BUNIT"]

        data = self.data.copy()

        xmin = - naxis1 / 2. * cdelt1
        xmax = naxis1 / 2. * cdelt1
        ymin = - naxis2 / 2. * cdelt2
        ymax = naxis2 / 2. * cdelt2

        if vmin is None :
            if content == "CONTINUUM INTENSITY" :
                vmin = 0
            elif content == "MAGNETOGRAM" :
                vmin = -100
            elif content == "DOPPLERGRAM" :
                vmin = -10000
        if vmax is None :
            if content == "CONTINUUM INTENSITY" :
                vmax = 65535
            elif content == "MAGNETOGRAM" :
                vmax = 100
            elif content == "DOPPLERGRAM" :
                vmax = 10000

        data[np.isnan(data)] = vmin

        plt.figure()
        plt.imshow(data, vmin=vmin, vmax=vmax, extent = [xmin, xmax, ymin, ymax], cmap="gray")
        plt.title(f"{telescop} {content} {t_rec}")
        plt.xlabel(cunit1)
        plt.ylabel(cunit2)
        plt.colorbar(label=bunit)
        plt.show()        


class HMIContinuumDataset(HMIDataset):
    def __init__(self, filepath):
        super(HMIContinuumDataset, self).__init__(filepath)


class HMIDopplergramDataset(HMIDataset):
    def __init__(self, filepath):
        super(HMIDopplergramDataset, self).__init__(filepath)


class HMIMagnetogramDataset(HMIDataset):
    def __init__(self, filepath):
        super(HMIMagnetogramDataset, self).__init__(filepath)

