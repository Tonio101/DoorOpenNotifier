# DoorOpenAlert
RaspberryPi Door Open Alert<br/>
Simple switch connected to a RaspberryPi to notify<br/>
me when the door opens via text message.<br/>

### Parts needed:
- [Magentic Contact Switch](https://www.adafruit.com/product/375)<br/>
- RaspberryPi v 2|3 running the latest Raspbian.<br/>
- [Wemo Mini Smart Plug](https://www.belkin.com/us/p/P-F7C063/)<br/>


### Prereqs:
- Python2 or Python3<br/>
- [Follow this Tutorial to install pywemo](https://github.com/pavoni/pywemo)<br/>
- Configured/Enabled Bluetooth on the RaspberryPi.<br/>
  I won't go over this, so much documentation out there.<br/>

### Configure RaspberryPi to send messages:
```bash
  sudo apt-get install arp-scan

  sudo apt-get install ssmtp
  sudo apt-get install mailutils

  sudo vim /etc/ssmtp/ssmtp.conf
```
In this file include:<br/>
```bash
root=postmaster
mailhub=smtp.gmail.com:587
hostname=<YOURHOSTNAME>
AuthUser=<YOUREMAIL>
AuthPass=<YOURPASSWORD>
FromLineOverride=YES
UseSTARTTLS=YES
Debug=YES
```

Sending a text message:<br/>
You can find your service provider SMS gateway address [here](https://www.freecarrierlookup.com/)<br/>
```bash
  echo "Hello World!" | mail -s 'Test Subject' <PHONE_NUMBER>@tmomail.net
```
That's it! Now you can send text messages via command line.<br/>

### Usage example:
Very basic implementation.<br/>
```bash
  python door_open.py --mode [HOME|AWAY]
```
2 modes:<br/>
Set mode to HOME if you are home.<br/>
  In this mode, it will turn on the light automatically when the door opens during<br/>
  certain times of the day. It will also turn off the lights automatically if you<br/>
  are not home.<br/>

Set mode to AWAY if you are traveling.<br/>
  Create the illusion that someone is home while you are traveling.<br/>
