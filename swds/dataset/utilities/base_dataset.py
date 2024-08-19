import textwrap
#from abc import ABC, abstractmethod

class BaseDataset:#(ABC):
    """
    Base class for SWPy dataset
    """
    def __init__(self, filepath):
        """
        Initialize the dataset

        args:
            filepath: str
                path to the data file
        return:
            None        
        """
        self.filepath = filepath
        self.data = None
        self.header = None
        self.all = None

        self.institute = None
        self.observatory = None
        self.satellite = None
        self.instrument = None
        self.telescope = None
        self.detector = None
        self.model = None
        self.object = None
        self.date = None
        self.dimension = None
        self.data_num = None

    def info(self):
        info = textwrap.dedent(f"""\
            Institute: \t {self.institute}
            Observatory: \t {self.observatory}
            Satellite: \t {self.satellite}
            Instrument: \t {self.instrument}
            Telescope: \t {self.telescope}
            Detector: \t {self.detector}
            Model: \t\t {self.model}
            Object: \t {self.object}
            Date: \t\t {self.date}
            Dimension: \t {self.dimension}
            Data num: \t {self.data_num}
            """)
        print(info)
