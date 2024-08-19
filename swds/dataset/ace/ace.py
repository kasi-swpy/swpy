import textwrap
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from swpy.swds.dataset.utilities import BaseDataset
from swpy.swds.dataset.utilities import Header, All
from swpy.swds.dataset.utilities import BasePlot
from swpy.swds.dataset.utilities import Processor

def ace_open(data_all):
    """ 
    Read the header containing the file name, and assign the observation target and observation date.
    """
    firstline = data_all[0][0]
    if "mag" in firstline :
        dataset = MAGDataset(data_all)
    elif "sis" in firstline :
        dataset = SISDataset(data_all)
    elif "swepam" in firstline :
        dataset = SWEPAMDataset(data_all)
    else :
        raise NameError("Unknown ACE content")
    return dataset

class ACEDataset(BaseDataset):
    """
    Initialize the GOESDataset with the given file array, loading and parsing its content.
    """
    def __init__(self, data_all):
        super (ACEDataset, self).__init__(data_all)
        self.data_all = data_all
        self.header_delimiters = ["#", ":"]
        self.dict_delimiter = ":"

        self.institute = "NOAA"
        self.satellite = "ACE"
        self.observatory = "ACE"

        self.load()
        self.parsing_header()
        self.parsing_data()
        self.all = All(self.header, self.data)

    def load(self):
        """
        Parameters
        ----------
        filepath: numpy.ndarray
            file array to read
        
        Returns
        -------
        header_lines: list
            lines of header
        data_lines: list
            lines of data
        """
        header_lines = []
        data_lines = []

        # While reading data_all line by line,
        # if header_delimiters are found, separated into header_lines
        # otherwise, separated into data_lines.
        for i in range(len(self.data_all)):
            lines = self.data_all[i][0]

            if type(lines) is float and np.isnan(lines): 
                continue
            
            if lines[0] in self.header_delimiters:
                header_lines.append(lines)
            else:
                data_lines.append(lines)

        self.header_lines = header_lines
        self.data_lines = data_lines

    def parsing_header(self):
        header = Header()
        notes = []
        labels = []
        units = []
        prev_key = ""
        
        for i, line in enumerate(self.header_lines):
            
            # Separate the line containing the file name.
            if line[0] == self.dict_delimiter and line[1:9] == 'Data_list':
                header_value = line.split(':')[2].strip()
                header['Data_list'] = header_value
                header['Data_list'].append(header_value)
                
            # Remove header delimiters and both leading and trailing whitespace.
            if (any(dlmt == line[0] for dlmt in self.header_delimiters)):
                line = line[1:]

            # If the line has 2 or more leading whitespaces, it is considered as a value corresponding to the previous key.
            if (len(line)-len(line.lstrip()) < 2):
                prev_key = ""
            
            # Remove whitespace of head and tail.
            line = line.strip()

            # Skip from column to end.
            if(i >= len(self.header_lines)-3):
                continue
            
            # Process blank lines.
            if (line == ""):
                prev_key == ""
                continue

            # Put anything that is not in the key-value form in 'note'.
            if (self.dict_delimiter not in line):
                #add unfinished value of prev key
                if (prev_key != ""):
                    line = " {}".format(line)
                    if (prev_key == "Label"):
                        labels.append(labels.pop() + line)
                    elif (prev_key == "Units"):
                        units.append(units.pop() + line)
                    else:
                        header[prev_key] += line
                    continue
                
                notes.append(line)
                continue
               
            # Split the key and value based on the delimiter.
            key, value = line.split(self.dict_delimiter, 1)
            key = key.strip()
            value = value.strip()
            
        # Create a dictionary by linking keys and values. If a key has more than one value, they are assigned as a list.
            if key in header:
                if type(header[key]) is not list:
                    header[key] = [header[key]]
                header[key].append(value)
            else:
                header[key] = value  

        for key, value in [('Note',notes),('Label',labels),('Units',units)]:
            if value:
                if key in header:
                    header[key].extend(value)
                else:
                    header[key] = value

        # Remove duplicate parts from header["Note"].
        header["Note"] = list(dict.fromkeys(header["Note"]))
        header["Note"] = header["Note"][:-4]

        self.satellite = " ".join(sorted(set(header["Source"]), key=header["Source"].index))
        self.units = header["Units"]
        self.header = header

    def parsing_data(self):
        data = []
        date_format = "{0}-{1}-{2} {3}:{4}"

        for line in self.data_lines:
            if(line.strip == ""):
                continue
            
            # Split the line into componets.
            values = line.split()
            
            # year, month, day, hour, minute
            Y, m, d, HM = values.pop(0), values.pop(0), values.pop(0), values.pop(0)
            H, M = HM[:2], HM[2:]
           
            # Format the date and convert it to a datetime object.
            date = date_format.format(Y, m, d, H, M)
            date_time = datetime.strptime(date, '%Y-%m-%d %H:%M')

            jd = values.pop(0)
            sd = values.pop(0)

            data_tuple = (date_time,)
            
            # 'Missing data values' are assigned as NaN.
            for value in values:
                if value == '-999.9':
                    data_tuple += (np.nan,)
                else:
                    data_tuple += (value,)
            
            data.append(data_tuple)

        # Assign the data based on the information received from the class containing the file save details.
        data = np.array(data, dtype={'names':self.names, 'formats':self.formats})
        self.dimension = data.shape
        self.data_num = data.size
        
        start_date = data["Date"][0]
        end_date = data["Date"][-1]
        self.date = f"Start date: {str(start_date)[:10]}, End date: {str(end_date)[:10]}"
        self.data = data
        
        return data

    def __repr__(self):
        rep = textwrap.dedent(f"""\
            -----------------------------------
            {self.date}
            {self.satellite} {self.instrument}
            header:\t\t dict
            data:\t\t structured array(np.ndarray)
            all:\t\t all(header, data)
            -----------------------------------
            """)
        return rep


"""
The class representing save details according to the observation object.
"""
class MAGDataset(ACEDataset, BasePlot):
    def __init__(self, data_all):
        self.names = ("Date", "Status", "Bx", "By", "Bz", "Bt", "Latitude", "Longitude")
        self.formats = ("datetime64[s]", "i2", "f8", "f8", "f8", "f8", "f8", "f8")
        super(MAGDataset, self).__init__(data_all)
        self.instrument = "MAG"
        self.detector = "MAG"
        self.object = "Magnetic Field"
        BasePlot.__init__(self, self.data, self.names, self.header)


class SISDataset(ACEDataset, BasePlot):
    def __init__(self, data_all):
        self.names = ("Date", "Status_10", "MeV_10", "Status_30", "MeV_30")
        self.formats = ("datetime64[s]", "i2", "f8", "i2", "f8")
        super(SISDataset, self).__init__(data_all)
        self.instrument = "SIS"
        self.detector = "SIS"
        self.object = "Solar Isotope Spectrometer"


class SWEPAMDataset(ACEDataset, BasePlot):
    def __init__(self, data_all):
        self.names = ("Date", "Status", "ProtonDensity", "BulkSpeed", "IonTemperature")
        self.formats = ("datetime64[s]", "i4", "f8", "f8", "f8")
        super(SWEPAMDataset, self).__init__(data_all)
        self.instrument = "SWEPAM"
        self.detector = "SWEPAM"
        self.object = "Solar Wind Electron Proton Alpha Monitor"