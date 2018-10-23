"""
Class to hold magic numbers, static data, Objects, etc...
"""
# run pinout for pin diagram
DOOR_SWITCH_PIN = 4

# trusted devices
LIST_OF_DEVICES = []

# SMS message type
MESSAGE_TYPE = 'ALERT'

ON = 1
OFF = 0

# Address of wemo switch
ADDRESS = '192.168.1.198'
#URL = 'http://192.168.1.198:{PORT}/setup.xml'

PHONE_NUMBERS = '<INSERT_YOUR_NUMBER>@tmomail.net, <INSERT_YOUR_NUMBER>@tmomail.net'

# Check devices connected to local network
ARP_CMD = "sudo arp-scan -l | grep '{ADDR}'"


class TrustedDevice(object):
    """
    Object representation of a Bluetooth Device.
    """
    def __init__(self, **kwargs):
        """
        Initialize of Bluetooth device
        """
        print(kwargs)
        for key in kwargs.keys():
            self.__setattr__(key, kwargs[key])
