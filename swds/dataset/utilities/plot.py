import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime

class BasePlot:
    """
    A method that receives the data processed by the parsing_data function and plots it.
    """
    def __init__(self, data, names, header):
        self.data = data
        self.names = names
        self.header = header

    def plot(self, start_time=None, end_time=None, target=None, sep_plots=True, figsize=None, log=True):
        """
        start_time, end_time : A feature that specifies plotting only for the set date and time.
        target : Plots only the targets entered as a list.
        sep_plots : A feature to choose between plotting multiple targets in one main plot or separate plots for each target.
        figsize : A feature to adjust the size of the plot image, with a default figsize of (12,6).
        log : A feature to set whether the plot scale is log or not.
        """

        # Convert the input time to datetime format.
        if start_time is not None:
            start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
        if end_time is not None:
            end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M')

        # Filter the data based on the provided time range.
        if start_time is not None or end_time is not None:
            if start_time is not None and end_time is not None:
                mask = (self.data["Date"] >= start_time) & (self.data["Date"] <= end_time)    
            elif start_time is not None:
                mask = self.data["Date"] >= start_time
            else:
                mask = self.data["Date"] <= end_time
            DATA = self.data[mask]
        else:
            DATA = self.data

        DATE = DATA["Date"]
        
        colors = plt.cm.tab20(np.linspace(0,1,len(self.names[1:])))
        unit_label = str(list(dict.fromkeys(self.header['Units']))).strip("[]")

        # Check if the target is all items or just the entered values, and assign it to the target variable.
        if target is None:
            target = self.names[1:]
        else:
            if isinstance(target,list):
                target = target
        
        #Set the plot content based on whether it’s one main plot or separate plots for each target.
        if sep_plots is False:    
            # One main plot
            if figsize is not None:
                plt.figure(figsize=figsize)
            else:
                plt.figure(figsize=(12,6))

            for name in target:
                plt.plot(DATE, DATA[name], label=name)

            if log is True:
                plt.yscale("log")

            plt.ylabel(f'Units: {unit_label}', labelpad=15)
            plt.title(self.header["Note"][-1])
        else:
            # Separate plots for each target
            if figsize is not None:
                fig, axs = plt.subplots(len(target), 1, figsize=figsize, sharex=True)
            else:
                fig, axs = plt.subplots(len(target), 1, figsize=(12, 6), sharex=True)

            if len(target) == 1:
                plt.plot(DATE, DATA[target], label=target)
            else:
                for i, (name,color) in enumerate(zip(target, colors[:len(target)])):
                    axs[i].plot(DATE, DATA[name], label=name, color=color)
                    axs[i].grid(linestyle='--')
                    axs[i].legend(loc='upper right')

                    if log is True:
                        axs[i].set_yscale("log")

            fig.text(0.04, 0.5, f'Units: {unit_label}', va='center', rotation='vertical')
            plt.suptitle(self.header["Note"][-1])
        
        plt.xlabel('Date (UTC)', fontsize=9, labelpad=10)

        plt.legend()
        plt.grid(linestyle='--')
        plt.xlim(DATE.min(), DATE.max())
        plt.xticks(fontsize=7, rotation=45)
        plt.show()