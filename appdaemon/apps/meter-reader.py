from site import USER_BASE
import appdaemon.plugins.hass.hassapi as hass
import time
import datetime
import serial
import json
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish



#
# MeaterReading App
#
# Args:
#

class MeterReading(hass.Hass):
    
  async def initialize(self):
    broker = '192.168.x.x'
    port = 1883
    delay = 10

    self.log("In initialize")
    client = mqtt.Client("client-id")
    client.on_connect = self.on_connect
    client.on_message = self.messageFunction
    client.username_pw_set("user","pass")
    client.connect(broker, port, delay)
    client.loop_start()
    await self.run_every_Test(client)



  def on_connect(self, client, userdata, flags, rc):
    """"""
    self.log("Connected with result code  {}".format(str(rc)))
    client.subscribe("/usb/energy_consumption_total")
    client.subscribe("/usb/energy_production_total")
    client.subscribe("/usb/power_consumption")
    client.subscribe("/usb/power_production")
    client.subscribe("/usb/consumption_phase_l1")
    client.subscribe("/usb/production_phase_l1")
    client.subscribe("/usb/consumption_phase_l2")
    client.subscribe("/usb/production_phase_l2")
    client.subscribe("/usb/consumption_phase_l3")
    client.subscribe("/usb/production_phase_l3")
    client.subscribe("/usb/voltage_phase_l1")
    client.subscribe("/usb/voltage_phase_l2")
    client.subscribe("/usb/voltage_phase_l3")
    client.subscribe("/usb/current_phase_l1")
    client.subscribe("/usb/current_phase_l2")
    client.subscribe("/usb/current_phase_l3")


  async def energy(self, client, val, val2, val3):
    id = await self.slugify(val3)
    sub = "/usb/" + id
    client.publish(sub, val)


  async def slugify(self, str):
    return str.replace(" ", "_").lower()

    
    
  async def run_every_Test(self, client): 
      self.ser = serial.Serial(
        port = '/dev/ttyUSB0',
        baudrate = 115200,              # 115200 bauds
        bytesize = serial.EIGHTBITS,    # 8bits
        parity = serial.PARITY_NONE,    # even parity
        stopbits = serial.STOPBITS_ONE, # 1 stop bit
        xonxoff = False,                # no flow control
        timeout = 5
      )

      ser = self.ser
      
      if ser.isOpen():
        while(1):
          try:
            x = ser.readline()
            await self.get_single(x, client)
          except Exception as e:
            self.log("Exception")
            self.log(e)
            self.log(x)
            pass
        ser.flush()
      
      ser.close()
      
  async def get_single(self, item, client):
    x = item.decode("utf-8")
    #self.log("in get_single: {}".format(x))

    usb = {
      "8-1": "energy consumption total",
      "8-2": "energy production total",
      "1": "power consumption",
      "2": "power production",
      "21": "consumption phase l1",
      "22": "production phase l1",
      "41": "consumption phase l2",
      "42": "production phase l2",
      "61": "consumption phase l3",
      "62": "production phase l3",
      "32": "voltage phase l1",
      "52": "voltage phase l2",
      "72": "voltage phase l3",
      "31": "current phase l1",
      "51": "current phase l2",
      "71": "current phase l3"
    }
    
    if ":" in x:
        cont = x.split(":", 1)[1]
        when = x.split(":", 1)[0]
        if when == "0-0":
          pass
        elif "." in cont:
          test = cont.split(".",1)[1]
          test2 = cont.split(".",1)[0]

          cont = test.split("(", 1)[1]
          sub = cont[:-1]
          sub1 = sub.split('*')[0]
          sub2 = sub.split('*')[1]
          sub2 = sub2.strip()
          sub2 = sub2[:-1]

          if test and test.startswith("7"):            
            if test2 in usb:
              await self.energy(client, sub1, sub2, usb[test2])
          elif test and test.startswith("8"):        
            if test2 == "1":
              await self.energy(client, sub1, sub2, usb["8-1"])
            elif test2 == "2":
              await self.energy(client, sub1, sub2, usb["8-2"])
          else:
            self.log("https://hanporten.se/svenska/protokollet/")
    else:
        self.log("Nytt")