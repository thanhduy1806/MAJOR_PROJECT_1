from flask import Flask, jsonify
import paho.mqtt.client as mqtt
import sqlite3
import json
from datetime import datetime
from flask_cors import CORS
from flask import request
app = Flask(__name__)
CORS(app)

# Khởi tạo SQLite database
def init_db():
    conn = sqlite3.connect('sensor_data.db') #ket noi voi file.db hoac tao moi neu chua co, moi lan muon truy cap .db thi phai connect
    c = conn.cursor()           #tao doi tuong chay SQL
    c.execute('''CREATE TABLE IF NOT EXISTS sensor_data 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  timestamp TEXT, 
                  data TEXT)''') #tao bang neu chua co
    conn.commit()
    conn.close()

# CAC BUOC LAM VIEC VOI DATABASE.db
# MO KET NOI TRUOC connect(file.db)
# CHUAN DOI TUONG DO DE THUC HIEN CAU LENH SQL, DUNG cursor()
# THUC HIEN CAC LENH TUONG TAC VOI BANG, DE TAC DONG DUOC CAC LENH THI DUNG CAI DOI TUONG VUA TAO MA DE THUC HIEN CAU LENH SQL
# DONG FILE: DUNG DOI TUONG LUC TA TAO DE KHOI DONG KET NOI, THI GIO DUNG DOI TUONG DO DONG KET NOI
#     +commit()
#     +close()
#HIEU DON GIAN THI NO CO 1 DOI TUONG QUAN LY TOI FILE .db, VA TU DOI TUONG DO TA TAO 1 DOI TUONG NHO BEN TRONG CO VAI TRO THUC HIEN CAC LENH



# Callback khi kết nối MQTT
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe("esp32/data")

# Callback khi nhận message từ MQTT
def on_message(client, userdata, msg):
    print("on_message called! msg id:", id(msg))
    data = json.loads(msg.payload.decode())
    print("Received data:", data)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Lưu vào SQLite
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    c.execute("INSERT INTO sensor_data (timestamp, data) VALUES (?, ?)", 
              (timestamp, json.dumps(data)))
    conn.commit()
    conn.close()

# Cấu hình MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("localhost", 1883, 60)  # mosquito
client.loop_start()

# API lấy dữ liệu mới nhất
@app.route('/api/latest', methods=['GET'])
def get_latest_data():
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    c.execute("SELECT timestamp, data FROM sensor_data ORDER BY id DESC LIMIT 1")
    result = c.fetchone()   #tra ve 1 tuple la (timeslap,data)
    conn.close()
    if result:
        return jsonify({"timestamp": result[0], "data": json.loads(result[1])})
    return jsonify({"error": "No data"}), 404

# API lấy dữ liệu lịch sử
@app.route('/api/history', methods=['GET'])
def get_history_data():
    #limit = request.args.get('limit', default=10, type=int)
    conn = sqlite3.connect('sensor_data.db')
    c = conn.cursor()
    c.execute("SELECT timestamp, data FROM sensor_data ORDER BY id DESC LIMIT 50")
    results = c.fetchall() #tra ve 1 list tuple
    conn.close()
    return jsonify([{"timestamp": r[0], "data": json.loads(r[1])} for r in results])

if __name__ == '__main__':
    init_db()  # Khởi tạo database
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)