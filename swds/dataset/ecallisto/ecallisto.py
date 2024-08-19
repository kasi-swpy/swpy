import textwrap
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from swpy.swds.dataset.utilities import BaseDataset
from swpy.swds.dataset.utilities import fits_header_to_Header, All

def ecallisto_open(filepath):
    dataset = ECallistoDataset(filepath)
    return dataset


class ECallistoDataset(BaseDataset):
    def __init__(self, filepath):
        super(ECallistoDataset, self).__init__(filepath)
        self.all = fits.open(filepath)
        self.hdu = fits.open(filepath)
        self.institute = "KASI"
        self.observatory = "KASI_Daejeon_Korea"
        self.telescope = "E-Callisto"
        self.instrument = "E-Callisto"


        self.parsing_header()
        self.parsing_data()

    def parsing_header(self):
        header = [fits_header_to_Header(self.hdu[0].header),
                  fits_header_to_Header(self.hdu[1].header)]
        self.object = "Solar Radio Flux Densities [MHz]"
        self.date = header[0]["DATE-OBS"]
        self.header = header

    def parsing_data(self):
        data = [self.hdu[0].data,
                self.hdu[1].data]
        self.dimension = [data[0].shape, data[1].shape]
        self.data_num = [data[0].size, data[1].size]
        self.data = data

    def __repr__(self):
        rep = textwrap.dedent(f"""\
            -----------------------------------
            {self.observatory} {self.telescope} {self.object} {self.date}
            header:\t\t list(dict, dict)
            data:\t\t list(np.ndarray, np.ndarray)
            all:\t\t astropy.io.fits.hdu.hdulist.HDUList
            -----------------------------------
            """)
        return rep

    def plot(self):
        """
        데이터 시각화 함수
        - data의 시간과 빈도 값을 불러와 x축, y축으로 설정하여 이미지 생성
        """
        time_data = self.data[1]['TIME'][0]
        frequency_data = self.data[1]['FREQUENCY'][0]

        x = time_data
        y = frequency_data
        data = self.data[0]

        plt.imshow(data, extent=(x.min(), x.max(), y.min(), y.max()), cmap='viridis')
        plt.xlabel('Time')
        plt.ylabel('Frequency')
        plt.title('e-CALLISTO sp 59')
        cbar = plt.colorbar()
        cbar.set_label('Value')
        plt.show()
