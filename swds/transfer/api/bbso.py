import os, sys
#sys.path.append("../lib")

sys.path.append(
    os.path.dirname(
        os.path.abspath(
            os.path.dirname(__file__))))

from lib.transfer import Transfer
from lib.utilities import *
from .utils import parsing_config

from datetime import datetime
from dateutil.relativedelta import relativedelta
from math import ceil
import os


def download(start_date = "", end_date = "", overwrite = False):
    now = datetime.utcnow()

    download_kasi_id = "download_bbso"
    config_dict=parsing_config(download_kasi_id)
    source_path = config_dict["source_path"]
    source_pattern = config_dict["source_pattern"]
    destination_path = config_dict["destination_path"]
    log_path = config_dict["log_path"]
    temporary_dir = config_dict["temporary_dir"]
    today = int(config_dict["today"])    

    tf = Transfer()
    # Set transfer object.
    tf.set_log_path(log_path)
    tf.set_temp_dir(temporary_dir)

    protocol = config_dict["protocol"]
    address = config_dict["address"]

    print(address)

    tf.ftp_connect(address)
    day_count = 1

    if(type(start_date) == int):
        start_date = str(start_date)
    if(type(end_date) == int):
        end_date = str(end_date)

    if(len(start_date) > 8):
        start_date = start_date[:8]
    if(len(end_date) > 8):
        end_date = end_date[:8]

    print(start_date, end_date)

    start_date_format = get_date_format_by_len(start_date)
    end_date_format = get_date_format_by_len(end_date)

    print(start_date_format, end_date_format)

    if(start_date_format == None or end_date_format == None):
        print("BBSO download() : Wrong date format. (start_date len : %s, end_date len: %s)"%(len(start_date), len(end_date)))
        return False

    try:
        start_d = datetime.strptime(start_date, start_date_format)
    except Exception as e:
        print(e)
        print("BBSO download() : Wrong start date.")
        return False
    try:
        end_d = datetime.strptime(end_date, end_date_format)
    except Exception as e:
        print(e)
        print("BBSO download() : Wrong end date.")
        return False



    #
    # 1. Set date (str to date)
    #

    # latest
    if(start_date == "" and end_date == ""):
        start_d = now
    
    # multi day
    elif(start_date != "" and end_date != ""):     
        if(end_date_format == "%Y"):
            end_d = datetime(end_d.year, 12, 31)
        elif(end_date_format == "%Y%m"):
            end_d = end_d + relativedelta(months=1, days=-1)
        
        if(start_d > end_d):
            print("BBSO download() : The end date comes before the start date.")
            return False
        delta = end_d - start_d
        day_count = delta.days + 1
        
    # one day
    else:
        if(end_date != ""):
            start_d = end_d
            start_date_format = end_date_format

        if(start_date_format == "%Y"):
            day_count = 365

        elif(start_date_format == "%Y%m"):
            end_d = start_d + relativedelta(months=1, days=-1)
            delta = end_d - start_d
            day_count = delta.days + 1

    date = start_d    
    for i in range(day_count):
        # Set date.
        # Set src_path, dst_path by date
        s_path = source_pattern
        d_path = destination_path
        s_path = date.strftime(s_path)
        d_path = date.strftime(d_path)

        print(s_path)
        print(d_path)        
        # Download file at dst dir.
        tf.ftp_download(s_path, d_path, overwrite=overwrite)
        date += relativedelta(days=1) 

    if(tf.ftp_check_connection):
        tf.ftp_disconnect()

    return True
    
    



    




def get_date_format_by_len(date):
    date_format = ""
    if(len(date) == 0):
        pass
    elif(len(date) == 4):
        date_format = "%Y"
    elif(len(date) == 6):
        date_format = "%Y%m"
    elif(len(date) >= 8):
        date_format = "%Y%m%d"
    else:
        date_format = None
    return date_format

# # download(parsing_config(), start_date = "", end_date = 2020)

# if __name__ == "__main__" :
#    download()
   #download(start_date="20210101", end_date="20210102")