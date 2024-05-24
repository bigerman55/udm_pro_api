import subprocess  # For executing a shell command
import json
import os
import datetime
from subprocess import PIPE, Popen
from udm_pro.udmp import UDM_PRO_API
from requests import get

WAN_DATA_DIR = "<REDACTED>"


def ping(host):
    try:
        subprocess.check_output(["ping", "-c", "1", "-s", "1000", f"{host}"])
        return True
    except subprocess.CalledProcessError:
        return False


def get_recent_wan_events():
    udm_client = UDM_PRO_API()
    wan_events = udm_client.get_recent_wan_events()
    return wan_events


def get_monitors():
    udm_client = UDM_PRO_API()
    wan_monitors = udm_client.get_wan_monitors()
    return wan_monitors


def get_wan_ip():
    ip = get('https://api.ipify.org').content.decode('utf8')
    print('My public IP address is: {}'.format(ip))
    return ip


def save_file(wan_stats):
    now_ts = str(datetime.datetime.now())
    for wan, metrics in wan_stats.items():
        with open(f'{WAN_DATA_DIR}{wan}-data-{now_ts}.json', 'w') as saved_file:
            saved_file.write(json.dumps(metrics))
    return


def collect_filenames():
    files = []
    for filename in os.listdir(WAN_DATA_DIR):
        if ".json" in filename:
            files.append(filename)
    return files


def collect_file_details(file_name=None):
    file_details = {}

    if file_name:
        with open(file_name, 'r') as f:
            filename = file_name.replace(WAN_DATA_DIR, '')
            contents = f.read()
            file_details.update(
                {
                    filename: contents
                }
            )
        return file_details

    for filename in os.listdir(WAN_DATA_DIR):
        if ".json" in filename:
            with open(os.path.join(WAN_DATA_DIR, filename), 'r') as f:
                contents = f.read()
                file_details.update(
                    {
                        filename: contents
                    }
                )
    return file_details

"""
^^^ file_details = 
{'WAN-data-2024-05-23 02:58:05.031828.json': '{"healthy_monitors": {"1.1.1.1": {"availability": 100.0, "avg_latency": 100, "type": "dns"}, "8.8.8.8": {"availability": 100.0, "avg_latency": 166, "type": "dns"}, "ping.ui.com": {"availability": 100.0, "avg_latency": 78, "type": "icmp"}}, "unhealthy_monitors": {}}',
 'WAN2-data-2024-05-23 02:58:05.031828.json': '{"healthy_monitors": {"1.1.1.1": {"availability": 100.0, "avg_latency": 100, "type": "dns"}, "8.8.8.8": {"availability": 100.0, "avg_latency": 166, "type": "dns"}, "ping.ui.com": {"availability": 100.0, "avg_latency": 78, "type": "icmp"}}, "unhealthy_monitors": {}}'}
"""


# Save file if needed, collect file if needed, return if emergency update is needed or not
# 
def handle_files(wan_stats):
    files = collect_filenames()
    now_ts = str(datetime.datetime.now())
    if files:
        for filename in files:
            if now_ts[0:13] in filename:  # If timestamp to the current hour is present
                return True # Tell loop to not alert
            else: # No filename with file from current hour
                save_file(wan_stats)  # save all files from wan_stats
                return False # Tell loop to alert
    else: # no files in dir
        save_file(wan_stats)  # save files
        return False # Tell loop to alert


# Testing Method:
# def main():
#     wan_events = get_recent_wan_events()

#     print(wan_events)
#     return


# if __name__ == "__main__":
#     main()
