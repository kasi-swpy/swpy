import textwrap
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from swpy.swds.dataset.utilities import BaseDataset
from swpy.swds.dataset.utilities import Header, All
from swpy.swds.dataset.utilities import BasePlot
from swpy.swds.dataset.utilities import Processor


def goes_open(data_all):
    """ 
    Read the header containing the file name, and assign the observation object and observation date.
    """
    firstline = data_all[0][0]
    year=int(firstline[12:16])

    # Starting from 2021, the file content changes,
    # so the data is assigned to different classes based on the year to parse it correctly.
    if "Gp_part" in firstline :
        if year<2021:
            dataset = ParticleDatasetFir(data_all)
        else:
            dataset = ParticleDatasetSec(data_all)

    elif "Gp_xr" in firstline :
        if year<2021:
            dataset = XrayDatasetFir(data_all)
        else:
            dataset = XrayDatasetSec(data_all)

    elif "Gp_mag" in firstline :
        if year<2021:
            dataset = GeoMagDatasetFir(data_all)
        else:
            dataset = GeoMagDatasetSec(data_all)
    else :
        raise NameError("Unknown GOES content")
    return dataset

class GOESDataset(BaseDataset):
    """
    Initialize the GOESDataset with the given file array, loading and parsing its content.
    """
    def __init__(self, data_all):
        super(GOESDataset, self).__init__(data_all)
        self.data_all = data_all
        self.header_delimiters = ["#", ":"]
        self.dict_delimiter = ":"

        self.institute = "NOAA"
        self.observatory = "GOES"

        self.load()
        self.parsing_header()
        self.parsing_data()
        self.all = All(self.header, self.data)

    def load(self):
        """
        Parameters
        ----------
        data_all: numpy.ndarray
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
        """
        Read the header information and categorize it into header, notes, labels, and units.
        """
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
            
            # Remove whitespace of head and tail
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
        header["Note"] = header["Note"][:-3]

        self.satellite = " ".join(sorted(set(header["Source"]), key=header["Source"].index))
        self.units = header["Units"]
        self.header = header
        
    def parsing_data(self):
        """
        Read the date and proceed with date format
        eg. YYYY-mm-ddTHH:MM:SS
        """
        data = []
        date_format = "{0}-{1}-{2} {3}:{4}"

        Julian = []
        Julian_format = "{0}-{1}"

        sat_num = []
        sat_num_format = "{0}"

        arcjet_flag = []
        arcjet_flag_format = "{0}"

        for line in self.data_lines:
            if(line.strip == ""):
                continue
            
            # Split the line into componets.
            values = line.split()

            # year, month, day, hour, minute
            Y, m, d, HM = values.pop(0), values.pop(0), values.pop(0), values.pop(0)
            H, M = HM[:2], HM[2:]

            # If the data follows the class below, extract the Julian day. 
            if isinstance(self, (ParticleDatasetFir, XrayDatasetFir, GeoMagDatasetFir)):
                CY, D = values.pop(0), values.pop(0)            
                julian = Julian_format.format(CY, D)
                Julian.append(julian)
            else:
                Julian = None

            # If the data follows the class below, extract the satellite number and arcjet flag.        
            if isinstance(self, (ParticleDatasetSec, XrayDatasetSec, GeoMagDatasetSec)):
                SAT = values.pop(0)
                
                if isinstance(self, GeoMagDatasetSec):
                    ARCF = values.pop(4)

                    arcjetflag = arcjet_flag_format.format(ARCF)
                    arcjet_flag.append(arcjetflag)
                else:
                    arcjet_flag = None

                satnum = sat_num_format.format(SAT)
                sat_num.append(satnum)
            else:
                sat_num = None
                arcjet_flag = None

            # Format the date and convert it to a datetime object.
            date = date_format.format(Y, m, d, H, M)
            date_time = datetime.strptime(date, '%Y-%m-%d %H:%M')
            
            data_tuple = (date_time,)

            # 'Missing data values' are assigned as NaN.
            for value in values:
                if value == '-1.00e+05':
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

        if Julian:
            self.julian = Julian[0]
        if sat_num and arcjet_flag:
            self.satellite_num = sat_num[0]
            self.arcjet_flag = arcjet_flag[0]

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
Files saved before 2021 are classified as Fir, and those saved after 2021 are classified as Sec.
"""
class ParticleDatasetFir(GOESDataset, BasePlot):
    def __init__(self, data_all):
        self.names = ("Date", "P>1", "P>5", "P>10", "P>30", "P>50", "P>100", "E>0.8", "E>2.0", "E>4.0")
        self.formats = ("datetime64[s]", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8")
        super(ParticleDatasetFir, self).__init__(data_all)
        self.instrument = "SEISS"
        self.detector = "SEISS"
        self.object = "Particle Fluxes"
        BasePlot.__init__(self, self.data, self.names, self.header)


class ParticleDatasetSec(GOESDataset, BasePlot):
    def __init__(self, data_all):
        self.names = ("Date", "P>1", "P>5", "P>10", "P>30", "P>50", "P>60", "P>100", "P>500", "E>2.0")
        self.formats = ("datetime64[s]", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8")
        super(ParticleDatasetSec, self).__init__(data_all)
        self.instrument = "SEISS"
        self.detector = "SEISS"
        self.object = "Particle Fluxes"
        BasePlot.__init__(self, self.data, self.names, self.header)


class XrayDatasetFir(GOESDataset, BasePlot):
    def __init__(self, data_all):
        self.names = ("Date", "Short", "Long")
        self.formats = ("datetime64[s]", "f8", "f8")
        super(XrayDatasetFir, self).__init__(data_all)
        self.instrument = "XRS"
        self.detector = "XRS"
        self.object = "X-ray Fluxes"
        BasePlot.__init__(self, self.data, self.names, self.header)


class XrayDatasetSec(GOESDataset, BasePlot):
    def __init__(self, data_all):
        self.names = ("Date", "Short", "Long")
        self.formats = ("datetime64[s]", "f8", "f8")
        super(XrayDatasetSec, self).__init__(data_all)
        self.instrument = "XRS"
        self.detector = "XRS"
        self.object = "X-ray Fluxes"
        BasePlot.__init__(self, self.data, self.names, self.header)


class GeoMagDatasetFir(GOESDataset, BasePlot):
    def __init__(self, data_all):
        self.names = ("Date", "Hp", "He", "Hn", "total")
        self.formats = ("datetime64[s]", "f8", "f8", "f8", "f8")
        super(GeoMagDatasetFir, self).__init__(data_all)
        self.instrument = "MAG"
        self.detector = "MAG"
        self.object = "Magnetic Field"
        BasePlot.__init__(self, self.data, self.names, self.header)


class GeoMagDatasetSec(GOESDataset, BasePlot):
    def __init__(self, data_all):
        self.names = ("Date", "Hp", "He", "Hn", "total")
        self.formats = ("datetime64[s]", "f8", "f8", "f8", "f8")
        super(GeoMagDatasetSec, self).__init__(data_all)
        self.instrument = "MAG"
        self.detector = "MAG"
        self.object = "Magnetic Field"
        BasePlot.__init__(self, self.data, self.names, self.header)        

