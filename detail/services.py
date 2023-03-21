from netaddr import IPNetwork
from detail.models import serverinfo
import socket

def validateip( ip):
    IP = ip
    ip = IPNetwork(IP)
    ip_list = list(ip)
    return ip_list

def is_valid_ip(ipaddress):
    address = ipaddress
    message = "success"
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False
    return message

def validate(serverinfo):
    arr = []
    serverdetail = serverinfo
    serializer = serverinfoSerializer(serverdetail).data
    arr.append(serializer)
    output = {"data": arr}
    return output

def initializevalues(ip):
    serverinfo.ip = ip
    serverinfo.hostname = "-"
    serverinfo.os = "-"
    serverinfo.osversion = "-"
    serverinfo.xroadcomponent = "-"
    serverinfo.xroadcomponentversion = "-"
    serverinfo.url = "-"
    serverinfo.endpoint = "-"

def validateserverdetails(userdetails):
    username = userdetails.get('username')
    print(username)
    if username == '':
        message = "username should not be empty"
        return message
    password = userdetails.get('password')
    if password == '':
        message="password should not be empty"
        return message
    ip = userdetails.get('ip')
    if ip == '':
        message='IP should not be empty'
        return message
    if((ip != '') and (password != '') and (username != '')):
        message = "Success"
        return message

