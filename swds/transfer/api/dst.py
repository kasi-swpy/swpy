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

    download_kasi_id = "download_dst"
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

    month_count = 1
    
    if(type(start_date) == int):
        start_date = str(start_date)
    if(type(end_date) == int):
        end_date = str(end_date)
    
    # Get YYYYMM from input date.
    if(len(start_date) > 6):
        start_date = start_date[:6]
    if(len(end_date) > 6):
        end_date = end_date[:6]

    start_date_format = get_date_format_by_len(start_date)
    end_date_format = get_date_format_by_len(end_date)

    if(start_date_format == None or end_date_format == None):
        print("DST download() : Wrong date format. (start_date len : %s, end_date len: %s)"%(len(start_date), len(end_date)))
        return False

    try:
        start_d = datetime.strptime(start_date, start_date_format)
    except Exception as e:
        print(e)
        print("DST download() : Wrong start date.")
        return False
    try:
        end_d = datetime.strptime(end_date, end_date_format)
    except Exception as e:
        print(e)
        print("DST download() : Wrong end date.")
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
        
        if(start_d > end_d):
            print("DST download() : The end date comes before the start date.")
            return False
        month_count = (end_d.year - start_d.year) * 12 + (end_d.month - start_d.month) + 1

    # one day
    else:
        if(end_date != ""):
            start_d = end_d
            start_date_format = end_date_format

        if(start_date_format == "%Y"):
            month_count = 12
            
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
    for i in range(month_count):
        rv = False
        # Set date.
        date = start_d + relativedelta(months=i)
        # Set src_path, dst_path by date
        s_path = date.strftime(source_path)
        d_path = date.strftime(destination_path)
        print(s_path)

        # if(dst_protocol == "local"):
        # Download file at dst dir.
        rv = tf.http_download(s_path, d_path, overwrite=True)

        # Change file contents to dst format in dst dir.
        if rv:
            convert_to_dst_format(d_path, tf.log_path)
        
        # else:            
        #     # Set temp path.
        #     filename = os.path.split(s_path)[1].split(".")[0]
        #     temp_path = tf.temp_dir + filename + ".tmp"

        #     # Download file at temp dir.
        #     tf.transfer(s_path, temp_path)

        #     # Change file contents to dst format in temp dir.
        #     convert_to_dst_format(temp_path, tf.log_path)

        #     # Upload file to dst dir.
        #     tf.transfer(temp_path, d_path)    

    return True


def convert_to_dst_format(file_path, log_path):
    alert_message("Start convert file to dst format : {}".format(file_path), log_path)   
    #
    # 1. Open file.
    #
    try:
        fp = open(file_path, 'rb')
    except Exception as e:
        message = "Dst() : Fail to open file.\r\n\t{}".format(file_path)
        alert_message(message, log_path)
        return False

    #
    # 2. Read file and get contents.
    #
    try:
        line = fp.readline().decode("utf-8")
        # Pass.
        while(line != "" and line != "<!-- ^^^^^ E yyyymm_part2.html ^^^^^ -->\n"):
            line = fp.readline().decode("utf-8")

        # Read and get contents.
        line = fp.readline().decode("utf-8")
        contents = line
        while(line != ""):
            line = fp.readline().decode("utf-8")
            if(line == "<!-- vvvvv S yyyymm_part3.html vvvvv -->\n"):
                break
            contents += line
    except: 
        message = "Dst() : Fail to read file.\r\n\t{}".format(file_path)
        alert_message(message, log_path)
        return False
    fp.close()

    # Remove file after read.
    os.remove(file_path)

    #
    # 3. Write contents to file.
    #

    # Open file.
    try:
        f = open(file_path, "w")
    except Exception as e:
        message = "Dst() : Fail to open file.\r\n\t{}".format(file_path)
        alert_message(message, log_path)
        return False

    # Write file.
    try:
        f.write(contents)
    except Exception as e:
        message = "Dst() : Fail to write file.\r\n\t{}".format(file_path)
        alert_message(message, log_path)
        os.remove(file_path)
        return False
    f.close()
    
    return True

def get_date_format_by_len(date):
    date_format = ""
    if(len(date) == 0):
        pass
    elif(len(date) == 4):
        date_format = "%Y"
    elif(len(date) >= 6):
        date_format = "%Y%m"
    else:
        date_format = None
    return date_format


#
# Run.
#

# 만일 start date 보다 end date 가 더 빠르면 -> error처리?
# download("./dst/%Y%mdst.txt", start_date = "20190305", end_date = "202006")
# download("ftp://221.145.179.221/dst_test/%Y%mdst.txt", start_date = "20190305", end_date = "202006", id = "user1", pw = "12341234", keep_session = True)
# realtime("./dst/%Y%mdst.txt", "00:03:00")
# realtime("./dst/%Y%mdst.txt")

# download(parsing_config(), start_date = "", end_date = "")

# download(parsing_config(), start_date = "202004", end_date = "202005")

# download("/NAS/ioGuard/vol7/swc/data/wdc/dst/%Y/%Y%m_dst_obs.txt", start_date="201905", end_date="202005")

## http -> https 로 바뀐 것 확인, url 접속 안 됨