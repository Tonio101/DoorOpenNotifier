#!/usr/bin/env python
"""
- Notify a user when the door is open.
- Turn on Wemo plug during set time and if someone is home.
- Turn off Wemo plug if no one is home.
"""
import time
from datetime import datetime
from subprocess import PIPE, Popen
import RPi.GPIO as GPIO
from model_data import *
import pywemo
import bluetooth as BT
import sys, getopt

URL = 'http://192.168.1.198:{PORT}/setup.xml'

def connect_to_wemo():
    """
    Connect to Wemo Mini Smart Plug
    """
    print("Connecting to wemo...")
    global DEVICE, PORT
    port = pywemo.ouimeaux_device.probe_wemo(ADDRESS)
    DEVICE = pywemo.discovery.device_from_description(URL.format(PORT=port), None)
    print("Connected to Wemo Device.")

def get_wemo_state():
    """
    Get the current state of Wemo Mini Smart Plug

    :return: 0 or 1, where 0 => OFF, 1 => ON
    """
    port = pywemo.ouimeaux_device.probe_wemo(ADDRESS)
    DEVICE = pywemo.discovery.device_from_description(URL.format(PORT=port), None)
    return DEVICE.get_state()

def cmdline(command):
    """
    Helper function to run CLI command.

    :param command: Command to run.
    :return: output
    """
    process = Popen(args=command,
                    stdout=PIPE,
                    shell=True)
    return process.communicate()[0]

def should_turn_on_light():
    """
    Based on the time of day, decide whether the
    lights should be turned on or off.

    :return: True or False based on the time of day.
    """
    curr_hour = int(datetime.now().hour)
    if curr_hour > 19:
        # 8 pm - 11 pm
        return True
    elif (curr_hour >= 0) and (curr_hour < 7):
        # Midnight - 6 am
        return True
    return False

def init():
    """
    Initialization.
    """
    # BCM Mode run 'pinout' via command line for pin details.
    GPIO.setmode(GPIO.BCM)
    time.sleep(0.1)

    # Pull up switch
    GPIO.setup(DOOR_SWITCH_PIN, GPIO.IN, GPIO.PUD_UP)
    time.sleep(0.1)

    print('Setting up Device')

    # Setup a list of trusted devices.
    nexus_6p = TrustedDevice(name='nexus6p',
                             blt_mac_addr='<BLUETOOTH_MAC_ADDRESS>',
                             mac_addr='<MAC_ADDRESS>',
                             nick_name='Blah')
    print('Setting up Device Done')
    iphone_6 = TrustedDevice(name='iphone6',
                             blt_mac_addr='<BLUETOOTH_MAC_ADDRESS>',
                             mac_addr='<MAC_ADDRESS>',
                             nick_name='Blah2')
    LIST_OF_DEVICES.append(nexus_6p)
    LIST_OF_DEVICES.append(iphone_6)

    #Connect to the wemo device
    connect_to_wemo()

def who_is_home():
    """
    Check if a trusted device is connected to the Pi.

    :return: If device found, return name, else None
    """
    for each_device in LIST_OF_DEVICES: # Check Bluetooth connectivity
        paired_device = BT.lookup_name(each_device.blt_mac_addr, timeout=5)
        if paired_device:
            paired_device = paired_device.replace(" ", "").lower()
            if each_device.name in paired_device:
                return each_device.nick_name

    for each_device in LIST_OF_DEVICES: # Check local network
        cmd_str = cmdline(ARP_CMD.format(ADDR=each_device.mac_addr.lower()))
        if not cmd_str:
            continue
        cmd_str = cmd_str.split()
        # [<IP>, <MAC>, <NAME>]
        if cmd_str[1] in each_device.mac_addr.lower():
            return each_device.nick_name
    # Found no devices via Bluetooth or local network
    return None

def send_text(person, curr_time):
    """
    Send text message stating that the front door is open.
    """
    message = ''
    if not person:
        message = 'FRONT DOOR OPEN! - {0}'.format(curr_time)
    else:
        message = '{0} just opened the door! - {1}'.format(person, curr_time)
    cmdline("echo '{MESSAGE}' | mail -s '{MSG_TYPE}' {PHONE}".format(MESSAGE=message,
                                                                     MSG_TYPE=MESSAGE_TYPE,
                                                                     PHONE=PHONE_NUMBERS))

def workout_time():
    """
    My workout time.
    """
    curr_time = datetime.now()
    if (curr_time.hour == 5 and curr_time.minute == 10):
        print("Workout time!")
        return True

def set_wemo_switch_state(state):
    """
    Turn ON/OFF the Wemo Mini Smart Plug.
    """
    if state:
        if should_turn_on_light() and not get_wemo_state():
            print("Turning on the lights...")
            DEVICE.set_state(ON)
    else:
        if get_wemo_state():
            print("Turning off the lights...")
            DEVICE.set_state(OFF)

def main(argv):
    """
    This is where all the magic comes together.
    """
    try:
        travel_mode = 'HOME'
        opts, args = getopt.getopt(argv, "hm:", ["mode="])
        for opt, arg in opts:
            if opt == '-h':
                print 'door_open.py --mode away'
                sys.exit()
            elif opt in ("-m", "--mode"):
                travel_mode = arg
        print ("Travel Mode: {0}".format(travel_mode))
        on_vacation = False if 'HOME' in travel_mode else True
        init()
        notify = True
        gym_time = False
        print("Testing off...")
        DEVICE.set_state(OFF)
        time.sleep(3)
        print("Testing on...")
        DEVICE.set_state(ON)
        time.sleep(3)
        print("Turning off...")
        DEVICE.set_state(OFF)
        time.sleep(3)
        person = None

        while True:
            if GPIO.input(DOOR_SWITCH_PIN): # Door open
                curr_time = datetime.now().strftime("%m-%d-%y %H:%M:%S")
                person = who_is_home()
                if person: # Detected a trusted device connected
                    set_wemo_switch_state(ON)
                else:
                    if not on_vacation:
                        set_wemo_switch_state(OFF)
                if notify: # Send text alert
                    send_text(person, curr_time)
                    notify = False
                time.sleep(3)
            else: # Door closed
                notify = True
                if not on_vacation:
                    if not who_is_home():
                        set_wemo_switch_state(OFF)
                    if workout_time():
                        set_wemo_switch_state(ON)
                time.sleep(3)
    except KeyboardInterrupt as error:
        GPIO.cleanup()
        print(error)
        sys.exit(2)
    except Exception as error:
        GPIO.cleanup()
        print(error)
        sys.exit(2)
    except getopt.GetoptError:
        GPIO.cleanup()
        print(error)
        sys.exit(2)

if __name__ == '__main__':
    main(sys.argv[1:])
