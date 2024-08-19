import json
import os

config_task_path = "./config/config_task.json"
config_task = json.load(open(config_task_path))

ids = ["download_swpc_curind",
       "download_swpc_dayind_latest",
       "download_swpc_dgd",
       "download_swpc_a_boutok",
       "download_swpc_dayind",
       "download_swpc_srs",
       "download_swpc_dayobs",
       "download_swpc_rsga",
       "download_swpc_sgas",
       "download_swpc_daypre",
       "download_swpc_aurora_power",
       "download_swpc_dsd"]

for download_task_id in ids :
    os.system(config_task[download_task_id]["exec"])