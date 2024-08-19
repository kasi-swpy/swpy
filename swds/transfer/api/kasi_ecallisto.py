import os, sys
#sys.path.append("../lib")

sys.path.append(
    os.path.dirname(
        os.path.abspath(
            os.path.dirname(__file__))))

from lib.transfer import Transfer
from lib.utilities import *
from .utils import parsing_config

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from math import ceil
import os


def convert_HMS_to_sec(H, M, S):
    sec = None
    try:
        sec = int(H)*60*60 + int(M)*60 + int(S)
    except Exception as e:
        return None
    return sec

def download(uid, start_date = "", end_date = "", uid_list = []):
    now = datetime.utcnow()

    download_kasi_id = "download_kasi_ecallisto_" + uid
    config_dict=parsing_config(download_kasi_id)
    source_path = config_dict["source_path"]
    source_pattern = config_dict["source_pattern"]
    destination_path = config_dict["destination_path"]
    log_path = config_dict["log_path"]
    temporary_dir = config_dict["temporary_dir"]
    period = config_dict["period"]
    today = int(config_dict["today"])   

    tf = Transfer()
    # Set transfer object.
    tf.set_log_path(log_path)
    tf.set_temp_dir(temporary_dir)

    protocol = config_dict["protocol"]
    address = config_dict["address"]
    username = config_dict["username"]
    password = config_dict["password"]

    print(address)

    tf.ftp_connect(address, username, password)
    
    start_date, end_date = change_str_to_date(start_date, end_date)

    start_d = start_date
    end_d = end_date

    period_HMS_sec = None
    try:
        # get sec of HMS of period, start_d, end_d
        period_list = period.split(":")
        period_HMS_sec = convert_HMS_to_sec(period_list[0], period_list[1], period_list[2])

        start_d_HMS_sec = convert_HMS_to_sec(start_d.hour, start_d.minute, start_d.second)
        end_d_HMS_sec = convert_HMS_to_sec(end_d.hour, end_d.minute, end_d.second)

        if(period_HMS_sec == None or start_d_HMS_sec == None or end_d_HMS_sec == None):
            alert_message("kasi_ecallisto_download() : Fail to convert HMS to sec.\n"+str(e), log_path)
            return False
        
        # set start_d, end_d to match the on-time of the period
        start_d -= timedelta(seconds=start_d_HMS_sec%period_HMS_sec)
        end_d -= timedelta(seconds=end_d_HMS_sec%period_HMS_sec)
        
    except Exception as e:
        alert_message("kasi_ecallisto_download() : Fail to get period.\n"+str(e), log_path)
        return False
    if(period_HMS_sec == None):
        alert_message("kasi_ecallisto_download() : Fail to get period.\n"+str(e), log_path)
        return False

    if(today == 0):
        start_d -= relativedelta(days=1)
        end_d -= relativedelta(days=1)

    date = start_d
    while(date <= end_d):
        s_path = date.strftime(source_pattern)


        # if data is not exist on time,
        # recover prev two data that are not saved in dst path
        if(not tf.ftp_check_connection()):
            return
        is_exist = tf.ftp_check_file_exist(s_path)
        if(not is_exist):
            e_d = date
            s_d = e_d - timedelta(seconds=period_HMS_sec*2)
            d = e_d

            count = 0
            while(d >= s_d):
                print(d)
                if(count > 2):
                    break
                
                s_p = d.strftime(source_pattern)
                if(not tf.ftp_check_file_exist(s_p)):
                    d -= timedelta(seconds=1)
                    continue
                
                d_p = d.strftime(destination_path)
                print(s_p)
                print(d_p)
                tf.ftp_download(s_p, d_p)

                d -= timedelta(seconds=1)

            date += timedelta(seconds=period_HMS_sec)
            continue


        d_path = date.strftime(destination_path)

        print(s_path)
        print(d_path)            
        recursive = False
        if(not ".fit" in s_path):
            recursive = True
        tf.ftp_download(s_path, d_path, recursive)


        if(".fit" in s_path):
            date += timedelta(seconds=period_HMS_sec)
            continue
        date += relativedelta(days=1) 

    if(tf.ftp_check_connection):
        tf.ftp_disconnect()
    
    return True