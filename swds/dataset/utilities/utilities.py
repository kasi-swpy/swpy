from abc import ABC, abstractmethod

class BaseDataset(ABC):
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

    @abstractmethod
    def parsing(self):

        pass

    @abstractmethod
    def parsing_header(self):
        """
        Parse the header of the data file
        """
        pass

    @abstractmethod
    def parsing_data(self):
        """
        Parse the data of the data file
        """
        pass

    @abstractmethod
    def parsing_all(self):
        """
        Create "ALL" Object
        """
        pass

    # @abstractmethod
    # def plot(self):
    #     """
    #     Plot the parsed data
    #     """
    #     pass

