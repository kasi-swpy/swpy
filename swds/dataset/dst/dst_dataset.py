"""
dst_dataset_2.py
"""
from swpy.swds.dataset.utilities import BaseDataset
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
 
class dstDataset(BaseDataset):
    def __init__(self, file_):
        super(dstDataset, self).__init__(file_)

    def parsing(self):
        data = []
        with open(self.file_, 'r') as file:
            for line in file:
                line_data = line.strip().split()
                if line_data:
                    n_data = []
                    for value in line_data:
                        try:
                            n_data.append(int(value))
                        except ValueError:
                            pass
                        if n_data:
                            data.append(n_data)

        print(data)

        DST = np.array(data)
        
        h = []
        d = []
        for lst in DST[2:]:
            f = lst[0]
            h.append(f)

            f_output = lst[1:]
            d.append(f_output)
      
        HEADER = np.array(h)
        DATA = np.array(d)

        self.parsing_header(HEADER)
        self.parsing_data(DATA)
        self.parsing_all() 
       
    def parsing_header(self, HEADER):
        self.header = HEADER
        
    def parsing_data(self, DATA):
        self.data =  DATA
        
    def parsing_all(self):
        all = [self.header, self.data]
        self.all = all 


        
class DSTDataset(dstDataset):
    def __init__(self, file_):
        super(DSTDataset, self).__init__(file_)
        
    def plot(self):
        day = self.header["DAY"]
        for i in range(len(self.header)):
            day = self.header[i]
            for j in range(len(self.data)):
                if j == 0:
                    data = self.data[0]
                elif j == self.header[i]:
                    data == self.data[j]
                    
                    plt.plot(day, data)
                    plt.show()
                    