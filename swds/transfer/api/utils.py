import json, os

def parsing_config(download_task_id):

    config_acquisition_path = "./config/config_acquisition.json"
    config_access_path = "./config/config_access.json"

    config_dict = {}
    with open(config_acquisition_path) as f :
        config_acquisition = json.load(f)
    config_acquisition = config_acquisition[download_task_id]
    config_dict.update(config_acquisition)
    with open(config_access_path) as f :
        config_access = json.load(f)
    config_access = config_access[config_acquisition["access_id"]]
    config_dict.update(config_access)

    protocol = config_dict["protocol"]
    address = config_dict["address"]
    port = config_dict["port"]
    source_pattern = config_dict["source_pattern"]
    if port is not None :
        address = "%s:%s"%(address, port)
        config_dict["address"] = address
        source_path = "%s://%s:%s/%s"%(protocol, address, port, source_pattern)
    else :
        source_path = "%s://%s/%s"%(protocol, address, source_pattern)
    config_dict["source_path"] = source_path

    return config_dict


if __name__ == "__main__" :

    import sys

    sys.path.append("../config_original")

    download_task_id = "download_kasi_asc_fits"
    #download_task_id = "download_bbso"
    config_acquisition_path = "config_acquisition.json"
    config_access_path = ".config_access.json"

    config = parsing_config(download_task_id)

    print(config)
    port = config["port"]
    print(port)
    print(type(port))
