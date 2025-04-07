from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime





app = Flask(__name__)
socketio = SocketIO(app, async_mode='threading')  # Thêm async_mode

mqtt_data = {
    "led1": "0",
    "led2": "0"
}
status_time = {
    "led1": {"state": "0", "time": ""},
    "led2": {"state": "0", "time": ""}
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(" MQTT KẾT NỐI THÀNH CÔNG")
        client.subscribe("esp32/led_status")  # Đăng ký lắng nghe chủ đề
    else:
        print(f" MQTT KẾT NỐI THẤT BẠI, MÃ LỖI: {rc}")

def on_message(client, userdata, msg):
    global mqtt_data
    try:
        payload = json.loads(msg.payload.decode())
        mqtt_data.update(payload)
        print(f" Nhận từ MQTT: {payload}")
        # Lấy thời gian hiện tại
        now = datetime.now()
        # Chuyển thành chuỗi định dạng HH:MM:SS
        time_str = now.strftime("%H:%M:%S")
        # Lưu trạng thái + thời gian
        status_time['led1'] = {"state": mqtt_data['led1'], "time": time_str}
        status_time['led2'] = {"state": mqtt_data['led2'], "time": time_str}
        socketio.emit('update_led_status', mqtt_data)
        socketio.emit('statust_time',status_time)
        print(f"GUI LEN SOCKET LIST {status_time}")
    except Exception as e:
        print(f" Lỗi xử lý MQTT: {e}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message  # Đăng ký callback
mqtt_client.connect("192.168.1.10", 1883, 60)
mqtt_client.loop_start()

@app.route('/')
def index():
    return render_template('index.html', data=mqtt_data)

@socketio.on('change_status_led')
def handle_change_topic(data):
    global mqtt_data
    led1_status = data.get("led1", mqtt_data["led1"])
    led2_status = data.get("led2", mqtt_data["led2"])

    if led1_status != mqtt_data["led1"]:
        mqtt_data["led1"] = led1_status
        print(f" LED1: {led1_status}")
    if led2_status != mqtt_data["led2"]:
        mqtt_data["led2"] = led2_status
        print(f" LED2: {led2_status}")

    payload = json.dumps(mqtt_data)
    mqtt_client.publish("esp32/led_status", payload)
    print(f" Đã gửi lên MQTT: {payload}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
