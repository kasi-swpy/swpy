import textwrap
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from swpy.swds.dataset.utilities import BaseDataset
from swpy.swds.dataset.utilities import byte_scale
from swpy.swds.dataset.utilities import All, fits_header_to_Header


def bbso_open(filepath):
    dataset = BBSODataset(filepath)
    return dataset
    
class BBSODataset(BaseDataset):
    def __init__(self, filepath):
        super(BBSODataset, self).__init__(filepath)
        self.all = fits.open(filepath)
        self.hdu = fits.open(filepath)[0]

        self.parsing_header()
        self.parsing_data()

        self.institute = "BBSO"
        self.observatory = "BBSO"
        self.instrument = "BBSO H-alpha"
        self.object = "Sun"


    def parsing_header(self):
        if "WAVE ERR" in self.hdu.header.keys():
            self.hdu.header["WAVE_ERR"] = self.hdu.header["WAVE ERR"]
            del self.hdu.header["WAVE ERR"]
        header = fits_header_to_Header(self.hdu.header)
        self.date = header["DATE_OBS"]        
        self.header = header

    def parsing_data(self):
        data = self.hdu.data
        self.dimension = data.shape
        self.data_num = data.size
        self.data = data

    def __repr__(self):
        rep = textwrap.dedent(f"""\
            -----------------------------------
            {self.instrument} {self.date}
            header:\t\t dict
            data:\t\t np.ndarray
            all:\t\t astropy.io.fits.hdu.hdulist.HDUList
            -----------------------------------
            """)
        return rep
    
    def plot(self, **kwargs):
        plt.imshow(self.data, **kwargs)
        plt.show()
