import subprocess  # For executing a shell command
from subprocess import PIPE, Popen
from udm_pro.udmp import UDM_PRO_API


def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Building the command. Ex: "ping -n 1 google.com"
    command = f"ping -c 1 -s 1000 {host}"

    return subprocess.call(command) == 0


def traceroute(host):
    """
    Returns traceroute output to a particular host or ip as a string variable.
    """

    command = ['traceroute', '-4', host]
    with Popen(command, stdout=PIPE, stderr=None, shell=True) as process:
        output = process.communicate()[0].decode("utf-8")
        print(output)

    return output


def get_recent_wan_events():
    udm_client = UDM_PRO_API()
    wan_events = udm_client.get_recent_wan_events()
    return wan_events
