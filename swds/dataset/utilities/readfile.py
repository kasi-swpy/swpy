import os
import io
import glob
import zipfile
import requests
import textwrap
import numpy as np
from swpy.swds.dataset.utilities import BaseDataset
from swpy.swds.dataset.utilities import Header, All
from swpy.swds.request.request import search, Downloader

class Processor:
    """
    The class that reads data from the database in conjunction with 'swds.request.request'.
    """
    # Assign the 'request.search' function information to 'self.Downloader'.
    def __init__(self, search):
        self.Downloader = search

    def db_search(self):
        # Change the keyword from 'search', which finds file information from the URL, to 'download', which handles the file download function.
        url = self.Downloader.url.replace('search','download')
        
        # Store the downloaded zip file in the 'data_all' variable memory.
        try:
            response = requests.get(url)
            response.raise_for_status()

            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                data_all = np.full((1460*8,1), np.nan, dtype=object)
                file_idx = 0
                
                for file in z.namelist():
                    with z.open(file) as f:
                        data = f.read()
                        try:
                            text = data.decode('utf-8')
                            lines = text.splitlines()

                            for i, line in enumerate(lines[:1460]):
                                data_all[i + file_idx*1460, 0] = line.strip()
                            file_idx += 1
                        
                        except Exception as e:
                            print(f"Failed to process file {file}: {e}")
            return data_all

        except requests.exceptions.RequestException as e:
            print("Error occured:", e)


def data_local(filepath, keyword):
    """
    The function that reads data from the local.
    """

    # If multiple satellite data files in the focal folder,
    # entering the satellite keyword from the file name will allow you to read only the corresponding .txt files" 
    keyword = f'*{keyword}*.txt'
    file_list = glob.glob(os.path.join(filepath, keyword))
    
    start_day = str(input('Input start day (YYYYmmdd): '))
    set_day = int(input('Setting for the total plot day (1-7): '))
    if set_day > 7:
        print("Plot day can only be up to 7 days.\n")
        return None

    day = []
    for file in file_list:
        file_name = os.path.basename(file)
        day.append(file_name[:8])
    
    if start_day not in day:
        print(f"Start day '{start_day}' is not in the file.\n")
        return None

    index = 0
    data_all = np.full((1460*7,1), np.nan, dtype=object)

    for i in range(len(day)):
        if day[i] == start_day:
            file_path = file_list[i:i+(set_day)]
            for path in file_path:
                with open(path,'r') as f:
                    data = f.readlines()

                    for j, line in enumerate(data):
                        if index + j < data_all.shape[0]:
                            data_all[index + j, 0] = line.strip()
                    index += len(data)
        else:
            continue

    return data_all