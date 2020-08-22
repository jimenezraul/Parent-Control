#####################
# Parental Control #
####################
import paramiko
import time
from _datetime import datetime, timedelta

# Router ssh info
host = "Your router ip address"
port = 22
username = "Your router username"
password = "Your router password"

# Mac address to block
mac_to_block = ["Your:device:mac:address", "00:00:00:00:00:00"]


# Connect to the ssh server to get data
def connect():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
    return ssh


# Get Wireless leases list
def get_leases():
    ssh = connect()
    stdin, stdout, stderr = ssh.exec_command("cat /var/lib/misc/dnsmasq.leases")
    clients_list = [stdout.read().decode("utf-8").split("\n")]
    return clients_list


# Disconnect from ssh
def disconnect():
    ssh = connect()
    ssh.close()


# Make a Dict of the data
def get_clients_list():
    clients_list = get_leases()
    data = []
    for clients in clients_list:
        for i in range(len(clients) - 1):
            mac = clients[i].split()[1]
            ip_address = clients[i].split()[2]
            client_name = clients[i].split()[3]
            clients_info = {
                "mac": mac,
                "ip_address": ip_address,
                "name": client_name
            }
            data.append(clients_info)
    return data


# Check is the mac address on the mac_to_block match the mac on the data and append ip to the list
def get_data():
    return_data = get_clients_list()
    ip_list = []
    for client in return_data:
        for mac in mac_to_block:
            if client["mac"] == mac:
                ip_list.append(client["ip_address"])
    return ip_list


# Function to block ip
def blockIps(ip_list):
    ssh = connect()
    for ip in ip_list:
        block = f"iptables -I FORWARD -s {ip} -j DROP"
        ssh.exec_command(block)
    disconnect()


# Function to unblock ip
def unBlockIps(ip_list):
    ssh = connect()
    for ip in ip_list:
        unblock = f"iptables -D FORWARD -s {ip} -j DROP"
        ssh.exec_command(unblock)
    disconnect()


# Time Scheduling
while True:
    data_func = get_data()
    t = datetime.today()
    week_day = t.weekday()
    friday = 4
    saturday = 5
    # Check if is Friday or Saturday to block devices in a different time
    if week_day == friday or week_day == saturday:
        if t.hour < 21:
            # Weekend days block devices at 12pm
            future = datetime(t.year, t.month, t.day, 00, 00)
            future += timedelta(days=1)
            time.sleep((future - t).seconds)
            blockIps(data_func)
            time.sleep(1)
        else:
            # Weekend days unblock devices at 7am
            future = datetime(t.year, t.month, t.day, 7, 00)
            future += timedelta(days=1)
            time.sleep((future - t).seconds)
            unBlockIps(data_func)
            time.sleep(1)
    else:
        if t.hour < 21:
            # Week days block devices at 9pm
            future = datetime(t.year, t.month, t.day, 21, 00)
            future += timedelta(days=1)
            time.sleep((future - t).seconds)
            blockIps(data_func)
            time.sleep(1)
        else:
            # Week days unblock devices at 7am
            future = datetime(t.year, t.month, t.day, 7, 00)
            future += timedelta(days=1)
            time.sleep((future - t).seconds)
            unBlockIps(data_func)
            time.sleep(1)
