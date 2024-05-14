import subprocess  # For executing a shell command
from subprocess import PIPE, Popen
from udm_pro.udmp import UDM_PRO_API
from requests import get


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


def get_unhealthy_monitors():
    udm_client = UDM_PRO_API()
    unhealthy_monitors = udm_client.get_unhealthy_wan_monitors()
    return unhealthy_monitors


def get_wan_ip():
    ip = get('https://api.ipify.org').content.decode('utf8')
    print('My public IP address is: {}'.format(ip))
    return ip