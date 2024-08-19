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

    download_kasi_id = "download_nasa_" + uid
    config_dict=parsing_config(download_kasi_id)
    source_path = config_dict["source_path"]
    source_pattern = config_dict["source_pattern"]
    destination_path = config_dict["destination_path"]
    arm_path = config_dict["arm_path"]
    log_path = config_dict["log_path"]
    temporary_dir = config_dict["temporary_dir"]
    today = int(config_dict["today"])   

    tf = Transfer()
    # Set transfer object.
    tf.set_log_path(log_path)
    tf.set_temp_dir(temporary_dir)

    protocol = config_dict["protocol"]
    address = config_dict["address"]

    # src_addr = src_root.split("://")[1]
    
    start_d, end_d = change_str_to_date(start_date, end_date)
    print(start_d)
    print(end_d)


    src_path = source_path
    dst_path = destination_path
    arm_path = arm_path
    
    if(today == 0):
        start_d -= relativedelta(days=1)
        end_d -= relativedelta(days=1)

    date = start_d
    while(date <= end_d):  
        s_path = date.strftime(src_path)
        d_path = date.strftime(dst_path)
                    
        content = ""
        
        #
        # dst 처럼 download 받고 처리하면 좋겠지만 강제종료 시 해당 파일이 남는 것이 싫음 => 어쩔 수 없이 urllib 가져다 씀(바로 처리하려고)
        # get source content (consist of data filenames)
        #
        error_count = 0
        while(error_count <= 3):
            try:
                content = urllib.urlopen(s_path, timeout=30)
                break
            except Exception as e:
                if("HTTP Error 404: Not Found" in str(e)):
                    # print("http_download() : File is not existed.\r\n\t{}".format(src_path))
                    break
                # print("http_download() : Fail to call urlopen(1).\r\n\t{}".format(src_path))
                if(error_count == 3):
                    break
                error_count += 1
                time.sleep(4)

        #
        # contract data filenames from content
        #
        file_list = []
        try:
            line = content.readline().decode("utf-8")
            # Pass.
            while(line != "" and line != "   <tr><th colspan=\"5\"><hr></th></tr>\n"):
                line = content.readline().decode("utf-8")
            # line contains 'parent directory link'
            line = content.readline().decode("utf-8")
            while(line != ""):
                line = content.readline().decode("utf-8")
                if(line == "   <tr><th colspan=\"5\"><hr></th></tr>\n"):
                    break
                file = line.split("\"")[7]
                
                if(file[0] == "."):
                    continue
                
                file_list.append(file)

        except:
            date += relativedelta(days=1)
            continue
        
        if(not file_list):
            date += relativedelta(days=1)
            continue
        
        #
        # download files
        #
        for file in file_list:
            s_p = os.path.join(s_path, file)
            d_p = os.path.join(d_path, file)

            tf.http_download(s_p, d_p, overwrite=overwrite)


        #
        # latest files (only utcnow)
        #
        if(start_date == "" and end_date == ""):
            for file in reversed(file_list):
                if("1024.jpg" in file):
                    s_p = os.path.join(s_path, file)
                    tf.http_download(s_p, arm_path, overwrite=True)
                    break

        date += relativedelta(days=1)

# return True

if __name__ == "__main__" :

    config_path = "./config/test.json"
    config_dict = parsing_config(config_path)
    download([], config_dict, "20000101", "20000101")
