import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("KET NOI THANH CONG\n")
    else:
        print(f"KET NOI THAT BAI, MA LOI: {rc}")

client = mqtt.Client()
client.on_connect = on_connect

#Ket noi toi broker
client.connect("localhost",1883,60)
client.loop_start()

#Gui du lieu cach 5s
try:
    while True:
        message1 = "Du lieu tu client topic 1: "
        client.publish("test/topic1",message1)
        print(f"DA GUI MESSAGE TOPIC 1: {message1}")
        message2 = "Du lieu tu client topic 2: "
        client.publish("test/topic2",message2)
        print(f"DA GUI MESSAGE TOPIC 2: {message2}")
        time.sleep(2)
except KeyboardInterrupt:
    print("DUNG GUI DU LIEU")
    client.loop_stop()
    client.disconnect()