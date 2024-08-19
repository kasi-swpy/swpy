import sys
sys.path.append("../lib")
sys.path.append("../api")

import dst
import swpc
import kasi_asc
import kasi_mm
import kasi_mp
import kasi_ecallisto
import bbso
import nasa

from datetime import datetime, timedelta
import time
import os
import xml.etree.ElementTree as ET
import sys

import threading

from utilities import alert_message

dst_dict = {}
bbso_dict = {}
kasi_mp_dict = {}

dst_dict_origin = dst.parsing_config()
bbso_dict_origin = bbso.parsing_config()
kasi_mp_dict_origin = kasi_mp.parsing_config()

dst_dict["dst"] = dst_dict_origin
bbso_dict["bbso"] = bbso_dict_origin
kasi_mp_dict["kasi_mp"] = kasi_mp_dict_origin
swpc_dict = swpc.parsing_config()
kasi_asc_dict = kasi_asc.parsing_config()
kasi_mm_dict = kasi_mm.parsing_config()
kasi_ecallisto_dict = kasi_ecallisto.parsing_config()
nasa_dict = nasa.parsing_config()

kasi_mp_seconds = 0

def set_today(data_dict):
    for key, item in data_dict.items():
        if(key == "target"):
            continue
        if(int(item["today"]) == 0):
            item["today"] = 1

################################ 더 좋은 방법 찾기 ##############################
def replace_log_for_batch(data_dict, old, new):
    for key, item in data_dict.items():
        if(key != "target"):
            continue
        item["log_path"] = item["log_path"].replace(old, new)
#############################################################################


def get_download_list(data_dict):    
    try_datetime = None
    daily_datetime = None

    download_list = []
    for key, item in data_dict.items():
        if(key == "target"):
            continue

        now = datetime.utcnow()
        period = item["period"]
        t = item["time"]
        ### temp ####
        if(t == None):
            t = "11:30:00"

        #############
        try:
            try_datetime = item["try_datetime"]
        except:
            item["try_datetime"] = None
            try_datetime = None
        
        try:
            daily_datetime = item["daily_datetime"]

        except:
            item["daily_datetime"] = None
            daily_datetime = None

            if(t != None):
                h, m, s = t.split(":")
                daily_datetime = datetime(now.year, now.month, now.day, int(h), int(m), int(s))
                item["daily_datetime"] = daily_datetime

        rv = True
        if(try_datetime != None):
            td = now - try_datetime
            day_diff = td.days
            td = str(now - try_datetime)
            time_diff = td.split(".")[0]
            time_diff = "{:>08}".format(time_diff)
            if(day_diff > 0):
                time_diff = time_diff.split(", ")[1]
                hour_diff, t = time_diff.split(":", 1)
                hour_diff = int(hour_diff) + day_diff * 24
                time_diff = str(hour_diff) + ":" + t

            print(time_diff)
            print(period)
            if(time_diff < period):
                rv = False

        if not rv:
            if(daily_datetime != None):
                if(now.day != daily_datetime.day and now > daily_datetime):
                    daily_datetime = datetime(now.year, now.month, now.day, daily_datetime.hour, daily_datetime.minute, daily_datetime.second)
                    item["daily_datetime"] = daily_datetime
                td = now - daily_datetime
                day_diff = td.days
                print(now)
                print(daily_datetime)
                print(td)
                if(day_diff >= 0):
                    ####################################
                    log_path = "/SpaceWeatherPy/log/test_daily/%Y%m%d.log"
                    alert_message("[ now : "+str(now)+"    daily_datetime : "+str(daily_datetime)+" ] " + key + " is running.", log_path)
                    ####################################
                    rv = True
                    if(day_diff == 0):
                        day_diff += 1
                    item["daily_datetime"] = daily_datetime + timedelta(days=day_diff)
            if not rv:
                time.sleep(0.5)
                continue
        
        item["try_datetime"] = now

        download_list.append(key)
    return download_list

def kasi_mp_realtime():
    ###################### realtime stopped log #########################
    log_path = "/SpaceWeatherPy/log/realtime_program_stopped/download_sw_data.log"
    alert_message("kasi mp realtime is started", log_path)
    #############################################################
    try:
        while True:
            start = datetime.utcnow()
            status = kasi_mp.download()
            end = datetime.utcnow()
            #download_seconds = (end-start).seconds + (end-start).microseconds/1000000 - 0.02
            #time.sleep(kasi_mp_seconds-download_seconds)
            download_seconds = (end-start).seconds + (end-start).microseconds/1000000 - 0.1
            sleep_seconds = (kasi_mp_seconds-download_seconds)
            if(sleep_seconds < 0):
                sleep_seconds = 20
            try:
                time.sleep(sleep_seconds)
            except Exception as e:
                alert_message("Err: kasi mp realtime: "+str(e)+"\n\t\tsleep_seconds: "+sleep_seconds, log_path)
                time.sleep(20)
    ###################### realtime stopped log #########################
    except Exception as e:
        alert_message("kasi mp realtime is stopped: "+str(e), log_path)
        #############################################################
        time.sleep(1)
        kasi_mp_realtime()

def batch_all(start_date = "", end_date = ""):
    # change 'today' value to 1
    dst_dict_origin["today"] = 1
    bbso_dict_origin["today"] = 1
    kasi_mp_dict_origin["today"] = 1

    set_today(swpc_dict)
    set_today(kasi_asc_dict)
    set_today(kasi_mm_dict)
    set_today(kasi_ecallisto_dict)
    set_today(nasa_dict)

    ################################ 더 좋은 방법 찾기 ##############################
    old = "/SpaceWeatherPy/log/"
    new = "/SpaceWeatherPy/log/batch/"

    dst_dict_origin["log_path"] = dst_dict_origin["log_path"].replace(old, new)
    bbso_dict_origin["log_path"] = bbso_dict_origin["log_path"].replace(old, new)
    kasi_mp_dict_origin["log_path"] = kasi_mp_dict_origin["log_path"].replace(old, new)

    replace_log_for_batch(swpc_dict, old, new)
    replace_log_for_batch(kasi_asc_dict, old, new)
    replace_log_for_batch(kasi_mm_dict, old, new)
    replace_log_for_batch(kasi_ecallisto_dict, old, new)
    replace_log_for_batch(nasa_dict, old, new)
    #############################################################################

    dst.download(data_info_dict=dst_dict_origin, start_date=start_date, end_date=end_date)
    swpc.download(data_info_dict=swpc_dict, start_date=start_date, end_date=end_date)
    kasi_asc.download(data_info_dict=kasi_asc_dict, start_date=start_date, end_date=end_date, overwrite=True)
    kasi_mm.download(data_info_dict=kasi_mm_dict, start_date=start_date, end_date=end_date)
    kasi_ecallisto.download(data_info_dict=kasi_ecallisto_dict, start_date=start_date, end_date=end_date)
    bbso.download(data_info_dict=bbso_dict_origin, start_date=start_date, end_date=end_date, overwrite=True)
    nasa.download(data_info_dict=nasa_dict, start_date=start_date, end_date=end_date, overwrite=True)
    kasi_mp.download(data_info_dict=kasi_mp_dict_origin, start_date=start_date, end_date=end_date)

def realtime():
    ###################### realtime stopped log #########################
    log_path = "/SpaceWeatherPy/log/realtime_program_stopped/download_sw_data.log"
    alert_message("Realtime program is started", log_path)
    #############################################################

    try:
        while True:
            dst_download_list = get_download_list(dst_dict)
            swpc_download_list = get_download_list(swpc_dict)
            kasi_asc_download_list = get_download_list(kasi_asc_dict)
            kasi_mm_download_list = get_download_list(kasi_mm_dict)
            kasi_ecallisto_download_list = get_download_list(kasi_ecallisto_dict)
            bbso_download_list = get_download_list(bbso_dict)
            nasa_download_list = get_download_list(nasa_dict)

            print(dst_download_list)
            print(swpc_download_list)
            print(kasi_asc_download_list)
            print(kasi_mm_download_list)
            print(kasi_ecallisto_download_list)
            print(bbso_download_list)
            print(nasa_download_list)
                
            if(dst_download_list != []):
                dst.download()
            if(swpc_download_list != []):
                swpc.download(uid_list=swpc_download_list)
            if(kasi_asc_download_list != []):
                kasi_asc.download(uid_list=kasi_asc_download_list)
            if(kasi_mm_download_list != []):
                kasi_mm.download(uid_list=kasi_mm_download_list)
            if(kasi_ecallisto_download_list != []):
                kasi_ecallisto.download(uid_list=kasi_ecallisto_download_list)
            if(bbso_download_list != []):
                bbso.download()
            if(nasa_download_list != []):
                nasa.download()
    except Exception as e:
        ###################### realtime stopped log #########################
        alert_message("Realtime program is stopped: "+str(e), log_path)
        #############################################################
        time.sleep(1)
        realtime()

if __name__ == "__main__":
    argvs = sys.argv
    argvs.pop(0) # this program .py

    argvs_count = len(argvs)
    # realtime
    if(argvs_count == 0):
        kasi_mp_period = kasi_mp_dict_origin["period"]
        h, m, s = kasi_mp_period.split(":")
        kasi_mp_seconds = int(h) * 3600 + int(m) * 60 + int(s)
        
        ###################### realtime stopped log #########################
        log_path = "/SpaceWeatherPy/log/realtime_program_stopped/download_sw_data.log"
        alert_message("################ RUN PROGRAM ###############", log_path)
        #############################################################
        '''
        kasi_mp_thread = threading.Thread(target=kasi_mp_realtime)
        kasi_mp_thread.start()
        '''
        realtime()

    # batch - one day
    elif(argvs_count == 1):
        start_date = argvs.pop(0)
        try:
            int(start_date)
            start_date[3]
        except:
            exit("date type is wrong")
        batch_all(start_date)

    # batch - multi day
    elif(argvs_count == 2):
        start_date = argvs.pop(0)
        end_date = argvs.pop(0)

        try:
            int(start_date)
            int(end_date)
            start_date[3]
            end_date[3]
        except:
            exit("date type is wrong")
        batch_all(start_date, end_date)
    
    else:
        exit("argvs are too many")


