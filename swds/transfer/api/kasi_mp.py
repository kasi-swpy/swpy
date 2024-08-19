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


def download(start_date = "", end_date = ""):
    now = datetime.utcnow()

    download_kasi_id = "download_kasi_mp"
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

    if(type(start_date) == int):
        start_date = str(start_date)
    if(type(end_date) == int):
        end_date = str(end_date)

    if(len(start_date) > 12):
        start_date = start_date[:12]
    if(len(end_date) > 12):
        end_date = end_date[:12]

    start_date_format = get_date_format_by_len(start_date)
    end_date_format = get_date_format_by_len(end_date)


    if(start_date_format == None or end_date_format == None):
        print("KASI_MP download() : Wrong date format. (start_date len : %s, end_date len: %s)"%(len(start_date), len(end_date)))
        return False

    try:
        start_d = datetime.strptime(start_date, start_date_format)
    except Exception as e:
        print(e)
        print("KASI_MP download() : Wrong start date.")
        return False
    try:
        end_d = datetime.strptime(end_date, end_date_format)
    except Exception as e:
        print(e)
        print("KASI_MP download() : Wrong end date.")
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
            end_d = datetime(end_d.year, 12, 31, 23, 59)
        elif(end_date_format == "%Y%m"):
            end_d = end_d + relativedelta(months=1, days=-1)
            end_d = datetime(end_d.year, end_d.month, end_d.day, 23, 59)     
        elif(end_date_format == "%Y%m%d"):
            end_d = datetime(end_d.year, end_d.month, end_d.day, 23, 59)
        elif(end_date_format == "%Y%m%d%H"):
            end_d = datetime(end_d.year, end_d.month, end_d.day, end_d.hour, 59)

        if(start_d > end_d):
            print("KASI_MP download() : The end date comes before the start date.")
            return False

        delta = end_d - start_d
        min_count = delta.days * 24 * 60 + int(delta.seconds / 60) + 1

    # one day
    else:
        if(end_date != ""):
            start_d = end_d
            start_date_format = end_date_format
        
        if(start_date_format == "%Y"):
            min_count = 527040 # (365+1) * 24 * 60
        elif(start_date_format == "%Y%m"):
            end_d = start_d + relativedelta(months=1, days=-1)
            end_d = datetime(end_d.year, end_d.month, end_d.day, 23, 59)     
            delta = end_d - start_d
            min_count = delta.days * 24 * 60 + int(delta.seconds / 60) + 1
        elif(start_date_format == "%Y%m%d"):
            min_count = 1440 # 24 * 60
        elif(start_date_format == "%Y%m%d%H"):
            min_count = 60 # 60
            
    if(today == 0):
        start_d -= relativedelta(days=1)
        
    # Get protocol from path.
    # dst_protocol = "local"
    # if("://" in dst_path):
    #     dst_protocol = dst_path.split("://")[0]
    
    #
    # 2. Donwload and convert format dst
    #
    # if(dst_protocol == "local"):
    #     keep_session = False
    #     id = ""
    #     pw = ""
    #     temp_path = ""

    # Download from Start date to end date (period : month).
    rv = False
    for i in range(min_count):
        # Set date.
        date = start_d + relativedelta(minutes=i)
        # Set src_path, dst_path by date
        s_path = source_path
        s_path = date.strftime(s_path)

        d_path = destination_path
        d_path = date.strftime(d_path)
        
        print(s_path)
        
        # if(dst_protocol == "local"):
        # Download file at dst dir.
        tf.http_download(s_path, d_path, overwrite=True)
        
        # else:
        #     # Set temp path.
        #     filename = os.path.split(s_path)[1].split(".")[0]
        #     temp_path = tf.temp_dir + filename + ".tmp"

        #     # Download file at temp dir.
        #     rv = tf.transfer(s_path, temp_path)
                
        #     # Upload file to dst dir.
        #     rv = tf.transfer(temp_path, d_path)    
    
    return True

def get_date_format_by_len(date):
    date_format = ""
    if(len(date) == 0):
        pass
    elif(len(date) == 4):
        date_format = "%Y"
    elif(len(date) == 6):
        date_format = "%Y%m"
    elif(len(date) == 8):
        date_format = "%Y%m%d"
    elif(len(date) == 10):
        date_format = "%Y%m%d%H"
    elif(len(date) >= 12):
        date_format = "%Y%m%d%H%M"
    else:
        date_format = None
    return date_format