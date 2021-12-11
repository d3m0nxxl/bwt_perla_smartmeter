
# created by d3monxxl 

from vncdotool import api
import time
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import re
import paho.mqtt.client as mqtt

bwt_ipaddress = "192.168.0.247"
bwt_password="passwd"
mqtt_address="192.168.0.6"
mqtt_topic_throughput="/raspberrypi1/smartmeter/bwt/durchfluss"
mqtt_topic_volume="/raspberrypi1/smartmeter/bwt/volumen"

#def bwt_connect():
vncclient = api.connect(bwt_ipaddress, password=None)

def bwt_login():
    vncclient.mouseMove(400,200)
    vncclient.mouseDown(1)
    vncclient.mouseUp(1)
    vncclient.mouseMove(400,100)
    vncclient.mouseDown(1)
    vncclient.mouseUp(1)
    vncclient.keyPress(bwt_password[0])
    vncclient.keyPress(bwt_password[1])
    vncclient.keyPress(bwt_password[2])
    vncclient.keyPress(bwt_password[3])
    vncclient.keyPress(bwt_password[4])
    vncclient.keyPress(bwt_password[5])
    vncclient.mouseMove(715,420)
    vncclient.mouseDown(1)
    vncclient.mouseUp(1)
    vncclient.mouseMove(630,430)
    vncclient.mouseDown(1)
    vncclient.mouseUp(1)
    time.sleep(1)

bwt_login()

mqttclient=mqtt.Client()
mqttclient.connect(mqtt_address, 1883, 20)
mqttclient.loop_start()
mqttclient.reconnect_delay_set(min_delay=1, max_delay=120)
throughput_old=-1
volume_old=-1
while True:
    # Capture regions
    vncclient.captureRegion('throughput.png',110,140,280,50)
    vncclient.captureRegion('volume.png',145,300,200,50)
    throughputocroutput=pytesseract.image_to_string(Image.open('throughput.png'),lang = 'eng',config = '-c page_separator=""')
    volumeocroutput=pytesseract.image_to_string(Image.open('volume.png'),lang = 'eng',config = '-c page_separator=""')
    #print("=============================")
    #print("OCR result troughput: ",throughputocroutput.strip())
    #print("OCR result volume: ",volumeocroutput.strip())
    ### Throughput
    #throughput=re.search('(.*)\|*[MIl1\|]/h', throughputocroutput)
    throughput=re.search('(.*)\|*./h', throughputocroutput)
    #print("Throughput regex:",throughput)
    if throughput:
        throughput=throughput.group(1)
        throughput=throughput.strip()
        if throughput=="O":
            throughput=0
        #print("Throughput:",throughput)
    else:
        print('OCR throughput failed')
        print('-----------------')
        print(throughputocroutput)
        print('-----------------')
        print(throughput)
        print('-----------------')
        print('Trying to re-login')
        bwt_login()
        print('-----------------')
    ### Volume
    volume=re.search('(.*)[Il1\|]', volumeocroutput)
    #print("Volume regex:",volume)
    if volume:
        volume=volume.group(1)
        volume=volume.strip()
        if volume=="O":
            volume=0
        #print("Volume:",volume)
    else:
        print('OCR Volume failed')
        print('-----------------')
        print(volumeocroutput)
        print('-----------------')
        print(volume)
        print('-----------------')
    # Keep VNC connection alive
    vncclient.mouseMove(400,0)
    vncclient.mouseDown(1)
    vncclient.mouseUp(1)
    if throughput!=throughput_old:
        #print("MQTT: Publish throughput: ",throughput)
        try:
            mqttclient.publish(mqtt_topic_throughput, payload=throughput, qos=1, retain=False)
        except:
            print("MQTT: Publish throughput failed!")
        throughput_old=throughput
    if volume!=volume_old:
        #print("MQTT: Publish volume:    ",volume)
        try:
            mqttclient.publish(mqtt_topic_volume, payload=volume, qos=1, retain=False)
        except:
            print("MQTT: Publish volume failed!")
        volume_old=volume




