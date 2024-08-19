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
import urllib.request as urllib
import time


def download(uid, start_date = "", end_date = "", overwrite = False):
    now = datetime.utcnow()

    download_kasi_id = "download_swpc_" + uid
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

    limited_days = 80

    protocol = config_dict["protocol"]
    address = config_dict["address"]

    tf.ftp_connect(address)
    

    # get start date, end date, iter count (date type) for batch
    ############################################################################
    # latest
    # if("%" not in src_path):
    #     start_date = ""
    #     end_date = ""
    
    day_count = 1

    if(type(start_date) == int):
        start_date = str(start_date)
    if(type(end_date) == int):
        end_date = str(end_date)
    
    if(len(start_date) > 8):
        start_date = start_date[:8]
    if(len(end_date) > 8):
        end_date = end_date[:8]

    start_date_format = get_date_format_by_len(start_date)
    end_date_format = get_date_format_by_len(end_date)

    if(start_date_format == None or end_date_format == None):
        print("SWPC download() : Wrong date format. (start_date len : %s, end_date len: %s)"%(len(start_date), len(end_date)))
        return False

    try:
        start_d = datetime.strptime(start_date, start_date_format)
    except Exception as e:
        print(e)
        print("SWPC download() : Wrong start date.")
        return False
    try:
        end_d = datetime.strptime(end_date, end_date_format)
    except Exception as e:
        print(e)
        print("SWPC download() : Wrong end date.")
        return False
    #
    # 1. Set date (str to date)
    #

    # latest
    if((start_date == "" and end_date == "")):
        start_d = now

    # multi day
    elif(start_date != "" and end_date != ""):     
        if(end_date_format == "%Y"):
            end_d = datetime(end_d.year, 12, 31)
        elif(end_date_format == "%Y%m"):
            end_d = end_d + relativedelta(months=1, days=-1)
        
        if(start_d > end_d):
            print("SWPC download() : The end date comes before the start date.")
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

    ############################################################################


    if(uid == "dsd"):
        download_dsd_with_merge(config_dict, start_date=start_date, end_date = end_date, tf = tf)

    else :

        src_path = source_pattern
        dst_path = destination_path

        date = datetime(start_d.year, start_d.month, start_d.day)

        d_count = day_count

        if("%" not in src_path):
            d_count = 1
            date = now
        
        if(today == 0):
            date -= relativedelta(days=1)
        
        limited_start_date = now - relativedelta(days=limited_days)
        if(date < limited_start_date):
            print("ASDFASDFADF")
            d_count = d_count - (limited_start_date - date).days
            date = limited_start_date


        print(d_count)

        # # Get protocol from path.
        # dst_protocol = "local"
        # if("://" in dst_path):
        #     dst_protocol = dst_path.split("://")[0]



        # Download from Start date to end date (period : month).
        prev_s_path = ""
        for i in range(d_count):
            if(prev_s_path == src_path):
                date += relativedelta(days=1)
                continue
            
            print(date)

            # Set src_path, dst_path by date
            s_path = src_path
            if("[uB3]" in s_path):
                month = date.strftime("%B").upper()
                month = month[:3]
                s_path = s_path.replace("[uB3]", month)
            s_path = date.strftime(s_path)

            d_path = dst_path
            if("[uB3]" in d_path):
                month = date.strftime("%B").upper()
                month = month[:3]
                d_path = d_path.replace("[uB3]", month)
            d_path = date.strftime(d_path)
            
            print(s_path)

            tf.ftp_download(s_path, d_path, overwrite=True)

            # Set date.
            date += relativedelta(days=1)
            prev_s_path = s_path


    if(tf.ftp_check_connection):
        tf.ftp_disconnect()
    return True

def download_dsd(data_info_dict, start_date = "", end_date = "", tf = None):
    uid = "dsd"

    now = datetime.utcnow()

    tf_existed = True
    if(tf == None):
        tf_existed = False
        address = data_info_dict["address"]
        log_path = data_info_dict["log_path"]
        temp_dir = data_info_dict["temporary_dir"]

        tf = Transfer()

        # Set transfer object.
        tf.set_log_path(log_path)
        tf.set_temp_dir(temp_dir)

        tf.ftp_connect(address)

    src_path = data_info_dict["source_path"]
    dst_path = data_info_dict["destination_path"]
    
    # get start date, end date, iter count (date type) for batch
    ####################################################################
    month_count = 1
    
    if(type(start_date) == int):
        start_date = str(start_date)
    if(type(end_date) == int):
        end_date = str(end_date)

    if(len(start_date) > 6):
        start_date = start_date[:6]
    if(len(end_date) > 6):
        end_date = end_date[:6]
    
    start_date_format = get_date_format_by_len(start_date)
    end_date_format = get_date_format_by_len(end_date)

    if(start_date_format == None or end_date_format == None):
        print("SWPC download_dsd() : Wrong date format. (start_date len : %s, end_date len: %s)"%(len(start_date), len(end_date)))
        return False
    
    try:
        start_d = datetime.strptime(start_date, start_date_format)
    except Exception as e:
        print(e)
        print("SWPC download_dsd() : Wrong start date.")
        return False
    try:
        end_d = datetime.strptime(end_date, end_date_format)
    except Exception as e:
        print(e)
        print("SWPC download_dsd() : Wrong end date.")
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
            print("SWPC download_dsd() : The end date comes before the start date.")
            return False
        month_count = (end_d.year - start_d.year) * 12 + (end_d.month - start_d.month) + 1

    # one day
    else:
        if(end_date != ""):
            start_d = end_d
            start_date_format = end_date_format

        if(start_date_format == "%Y"):
            month_count = 12

    ####################################################################
    print(month_count)
    
    # # Get protocol from path.
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
    prev_q = -1
    date = start_d
    for i in range(month_count):
        # Set date.
        q = get_quarter(date)
        if(prev_q == q):
            date += relativedelta(months=1)
            continue

        # Set src_path, dst_path by date
        s_path = src_path.replace("[q]", str(q))
        s_path = date.strftime(s_path)
        d_path = dst_path.replace("[q]", str(q))
        d_path = date.strftime(d_path)
        print(s_path)
        
        # if(dst_protocol == "local"):
            # Download file at dst dir.
        tf.ftp_download(s_path, d_path, overwrite=True)
        
        # else:
        #     # Set temp path.
        #     filename = os.path.split(s_path)[1].split(".")[0]
        #     temp_path = tf.temp_dir + filename + ".tmp"

        #     # Download file at temp dir.
        #     tf.transfer(s_path, temp_path)
                
        #     # Upload file to dst dir.
        #     tf.transfer(temp_path, d_path)    
        date += relativedelta(months=1)
        prev_q = q
        
    if(tf_existed == False):
        if(tf.ftp_check_connection):
            tf.ftp_disconnect()
    return True

def download_dsd_with_merge(data_info_dict, start_date = "", end_date = "", tf = None):
    uid = "dsd"

    now = datetime.utcnow()

    tf_existed = True
    if(tf == None):
        tf_existed = False
        address = data_info_dict["address"]
        log_path = data_info_dict["log_path"]
        temp_dir = data_info_dict["temporary_dir"]

        tf = Transfer()

        # Set transfer object.
        tf.set_log_path(log_path)
        tf.set_temp_dir(temp_dir)

        tf.ftp_connect(address)

    src_path = data_info_dict["source_path"]
    dst_path = data_info_dict["destination_path"]

    # get start date, end date, iter count (date type) for batch
    ####################################################################
    month_count = 1
    last_s_path = ""
    last_q = 0

    if(type(start_date) == int):
        start_date = str(start_date)
    if(type(end_date) == int):
        end_date = str(end_date)

    if(len(start_date) > 6):
        start_date = start_date[:6]
    if(len(end_date) > 6):
        end_date = end_date[:6]

    start_date_format = get_date_format_by_len(start_date)
    end_date_format = get_date_format_by_len(end_date)

    if(start_date_format == None or end_date_format == None):
        print("SWPC download_dsd_with_merge() : Wrong date format. (start_date len : %s, end_date len: %s)"%(len(start_date), len(end_date)))
        return False

    try:
        start_d = datetime.strptime(start_date, start_date_format)
    except Exception as e:
        print(e)
        print("SWPC download_dsd_with_merge() : Wrong start date.")
        return False
    try:
        end_d = datetime.strptime(end_date, end_date_format)
    except Exception as e:
        print(e)
        print("SWPC download_dsd_with_merge() : Wrong end date.")
        return False

    #
    # 1. Set date (str to date)
    #

    # latest
    if(start_date == "" and end_date == ""):
        start_d = now
        # if(start_d.month != 1):
            # start_d = datetime(start_d.year, 1, 1)
        end_d = now

    # multi day
    elif(start_date != "" and end_date != ""):
        
        if(end_date_format == "%Y"):
            end_d = datetime(end_d.year, 12, 31)
        
        if(start_d > end_d):
            print("SWPC download_dsd_with_merge() : The end date comes before the start date.")
            return False
        # if(start_d.month != 1):
            # start_d = datetime(start_d.year, 1, 1)
        # month_count = (end_d.year - start_d.year) * 12 + (end_d.month - start_d.month) + 1
        

    # one day
    else:
        if(end_date != ""):
            start_d = end_d
            start_date_format = end_date_format

        if(start_date_format == "%Y"):
            end_d = datetime(end_d.year, 12, 31)
            # month_count = 12
        
        # if(start_d.month != 1):
            # start_d = datetime(start_d.year, 1, 1)

        # month_count = (end_d.month - start_d.month) + 1
    if(start_d.month != 1):
        start_d = datetime(start_d.year, 1, 1)
    month_count = (end_d.year - start_d.year) * 12 + (end_d.month - start_d.month) + 1

    last_q = get_quarter(end_d)
    last_s_path = src_path.replace("[q]", str(last_q))
    last_s_path = end_d.strftime(last_s_path)
    ####################################################################

    # # Get protocol from path.
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
    file_path_list = []
    prev_q = -1
    date = start_d
    for i in range(month_count):
        q = get_quarter(date)

        if(prev_q == q):
            date += relativedelta(months=1)
            continue
        # Set src_path, dst_path by date
        s_path = src_path.replace("[q]", str(q))
        s_path = date.strftime(s_path)
        d_path = date.strftime(dst_path)
        
        print(s_path)

        # if(dst_protocol == "local"):
        d_temp_path = os.path.split(d_path)[0] + "/" + os.path.split(s_path)[1]
        file_path_list.append(d_temp_path)
        
        # Download file at dst dir.
        tf.ftp_download(s_path, d_temp_path, overwrite=True)
        
        if(q == 4 or s_path == last_s_path):
            convert_to_dsd_format(file_path_list, d_path, tf.log_path)
            
            file_path_list = []
        # else:
        #     # Set temp path.
        #     filename = os.path.split(s_path)[1].split(".")[0]
        #     temp_path = tf.temp_dir + filename + ".tmp"

        #     file_path_list.append(temp_path)

        #     # Download file at temp dir.
        #     tf.transfer(s_path, temp_path)
            
        #     if(q == 4 or s_path == last_s_path):
        #         filename = os.path.split(d_path)[1].split(".")[0]
        #         temp_path = tf.temp_dir + filename + ".tmp"
                
        #         convert_to_dsd_format(file_path_list, temp_path, tf.log_path)

        #         # Upload file to dst dir.
        #         tf.transfer(temp_path, d_path)    
        #         file_path_list = []
        
        # Set date.
        date += relativedelta(months=1)
        prev_q = q

    if(tf_existed == False):
        if(tf.ftp_check_connection):
            tf.ftp_disconnect()

    return True


def convert_to_dsd_format(file_path_list, dst_path, log_path):    
    alert_message("Start convert file to dsd format : {}".format(file_path_list), log_path)
    
    if(file_path_list == None or file_path_list == ""):
        return False
    if(len(file_path_list) == 0):
        # return True
        return False
    #
    # 1. Read dsd files and get contents
    #
    contents = ""
    i = 0
    for file_path in file_path_list:
        # Open a file.
        if not os.path.isfile(file_path):
            continue
        try:
            fp = open(file_path, 'rb')
        except Exception as e:
            message = "SWPC convert_to_dsd_format() : Fail to open file.\r\n\t{}".format(file_path)
            alert_message(message, log_path)
            return False

        # Read a file.
        try:
            if(i > 0):
                line = fp.readline().decode("utf-8")
                # Pass.
                while(line != "" and "#----" not in line):
                    line = fp.readline().decode("utf-8")

            # Read and get contents.
            line = fp.readline().decode("utf-8")
            contents += line
            while(line != ""):
                line = fp.readline().decode("utf-8")
                contents += line
        except: 
            message = "SWPC convert_to_dsd_format() : Fail to read source file.\r\n\t{}".format(file_path)
            alert_message(message, log_path)
            return False
        fp.close()


        i += 1        
    #
    # 2. Write contents to file.
    #
    if(i == 0):
        message = "SWPC convert_to_dsd_format() : All files in file_path_list do not exist.\r\n\t{}".format(file_path_list)
        alert_message(message, log_path)
        return False

    # Open file
    try:
        f = open(dst_path, "w")
    except Exception as e:
        message = "SWPC convert_to_dsd_format() : Fail to open file.\r\n\t{}".format(dst_path)
        alert_message(message, log_path)
        return False

    # Write file.
    try:
        f.write(contents)
    except Exception as e:
        message = "SWPC convert_to_dsd_format() : Fail to write file.\r\n\t{}".format(dst_path)
        alert_message(message, log_path)
        os.remove(dst_path)
        return False
    f.close()
    
    # Remove file after convert.
    for file_path in file_path_list:
        os.remove(file_path)
    return True

def get_quarter(date):
    month = date.month
    quarter = ceil(month/3)
    return quarter

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

# download("a_boutok", parsing_config(), "202003", "2020")
# download("a_boutok", parsing_config(), "202003", "202005")
# download("a_boutok", parsing_config(), "20200310", "20200523")
# download([], parsing_config(), "2018", "20210101")

# download_dsd(parsing_config(), start_date = "", end_date = "2020")
# download_dsd_with_merge(parsing_config(), start_date = "201903", end_date = "202009")
# download_dsd_with_merge(parsing_config(), start_date = "201804", end_date = "202002")

# download_dsd(parsing_config(), "20170213","2020")

# data_info_dict = parsing_config()
# download(data_info_dict = data_info_dict)

# download(["dsd"], data_info_dict)

# convert_to_dsd_format(["./test1.txt","./test2.txt","./test3.txt"], "./test.txt", "./test.log")