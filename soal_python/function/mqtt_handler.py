import paho.mqtt.client as mqtt
import json
import random
from datetime import datetime, timezone
import csv
import os
from .help import get_current_timestamp_gmt7, get_current_timestamp_utc

class MQTTClient:
    def __init__(self, broker="test.mosquitto.org", port=1883, topic_publish="mqtt/zidan/data", 
                 topic_subscribe="mqtt/zidan/command"):
        self.broker = broker
        self.port = port
        self.topic_publish = topic_publish
        self.topic_subscribe = topic_subscribe
        self.client = None
        self.is_connected = False
        self.is_active = True
        self.interval = 5
        self.csv_file = None
        
    def on_connect(self, client, userdata, flags, reason_code, properties=None):
        """Callback ketika terhubung ke broker MQTT"""
        if reason_code == 0:
            self.is_connected = True
            print(f"{get_current_timestamp_gmt7()} - Connected to MQTT Broker: {self.broker}")
            # Subscribe ke topic command
            client.subscribe(self.topic_subscribe)
            print(f"{get_current_timestamp_gmt7()} - Subscribed to topic: {self.topic_subscribe}")
        else:
            print(f"{get_current_timestamp_gmt7()} - Failed to connect, reason code: {reason_code}")
            self.is_connected = False
    
    def on_message(self, client, userdata, msg):
        """Callback ketika menerima message"""
        try:
            payload = msg.payload.decode()
            data = json.loads(payload)
            
            print(f"{get_current_timestamp_gmt7()} | Action: Subscribe | Topic: {msg.topic} | Data: {data}")
            
            # Process command
            if 'command' in data:
                self.process_command(data['command'])
                
        except Exception as e:
            print(f"{get_current_timestamp_gmt7()} - Error processing message: {e}")
    
    def on_publish(self, client, userdata, mid, reason_code=None, properties=None):
        """Callback ketika publish berhasil"""
        # Callback ini akan dipanggil ketika publish berhasil
        pass
    
    def process_command(self, command):
        """Process command dari subscribe"""
        try:
            if command == "pause":
                self.is_active = False
                print(f"{get_current_timestamp_gmt7()} - Command received: PAUSE")
            elif command == "resume":
                self.is_active = True
                print(f"{get_current_timestamp_gmt7()} - Command received: RESUME")
            elif command.startswith("set_interval:"):
                try:
                    new_interval = int(command.split(":")[1])
                    if new_interval > 0:
                        self.interval = new_interval
                        print(f"{get_current_timestamp_gmt7()} - Command received: SET_INTERVAL to {new_interval}s")
                    else:
                        print(f"{get_current_timestamp_gmt7()} - Invalid interval value: {new_interval}")
                except ValueError:
                    print(f"{get_current_timestamp_gmt7()} - Invalid interval format")
            else:
                print(f"{get_current_timestamp_gmt7()} - Unknown command: {command}")
                
        except Exception as e:
            print(f"{get_current_timestamp_gmt7()} - Error processing command: {e}")
    
    def connect(self):
        """Connect ke MQTT broker"""
        try:
            self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_publish = self.on_publish
            
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"{get_current_timestamp_gmt7()} - Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect dari MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
    
    def get_weather_data(self):
        """Mendapatkan data weather terbaru dari JSON file"""
        try:
            json_file = "log/data_weather.json"
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                if data and len(data) > 0:
                    latest_data = data[-1]
                    return latest_data.get('temperature', 0.0), latest_data.get('humidity', 0.0)
            
            return 0.0, 0.0
        except Exception as e:
            print(f"{get_current_timestamp_gmt7()} - Error reading weather data: {e}")
            return 0.0, 0.0
    
    def generate_sensor_data(self):
        """Generate random sensor data"""
        sensor1 = random.randint(0, 100)          # Integer 0-100
        sensor2 = round(random.uniform(0, 1000), 2)  # Float 0-1000
        sensor3 = random.choice([True, False])    # Boolean
        sensor4, sensor5 = self.get_weather_data()  # Temperature & Humidity dari file JSON
        
        return sensor1, sensor2, sensor3, sensor4, sensor5
    
    def create_csv_logger(self):
        """Membuat file CSV logger"""
        try:
            log_dir = "log"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Format filename: mqtt_log_YYYYMMDD.csv
            date_str = datetime.now().strftime("%Y%m%d")
            filename = f"mqtt_log_{date_str}.csv"
            filepath = os.path.join(log_dir, filename)
            
            # Check if file exists, if not create with header
            if not os.path.exists(filepath):
                with open(filepath, 'w', newline='') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow(['timestamp', 'sensor1', 'sensor2', 'sensor3', 'sensor4', 'sensor5', 'status'])
            
            self.csv_file = filepath
            return True
        except Exception as e:
            print(f"{get_current_timestamp_gmt7()} - Error creating CSV logger: {e}")
            return False
    
    def log_to_csv(self, timestamp, sensor1, sensor2, sensor3, sensor4, sensor5, status):
        """Log data ke CSV file"""
        try:
            if self.csv_file:
                with open(self.csv_file, 'a', newline='') as f:
                    writer = csv.writer(f, delimiter=';')
                    writer.writerow([timestamp, sensor1, sensor2, sensor3, sensor4, sensor5, status])
                return True
            return False
        except Exception as e:
            print(f"{get_current_timestamp_gmt7()} - Error logging to CSV: {e}")
            return False
    
    def publish_data(self):
        """Publish data ke MQTT broker"""
        if not self.is_active:
            print(f"{get_current_timestamp_gmt7()} | Action: Publish | State: Inactive")
            return False
        
        if not self.is_connected:
            print(f"{get_current_timestamp_gmt7()} | Action: Publish | State: Failed (Not connected)")
            return False
        
        try:
            # Generate sensor data
            sensor1, sensor2, sensor3, sensor4, sensor5 = self.generate_sensor_data()
            
            # Prepare payload
            payload = {
                "nama": "Zidan",
                "data": {
                    "sensor1": sensor1,
                    "sensor2": sensor2,
                    "sensor3": sensor3,
                    "sensor4": sensor4,
                    "sensor5": sensor5
                },
                "timestamp": get_current_timestamp_utc()
            }
            
            json_payload = json.dumps(payload)
            
            # Publish to MQTT
            result = self.client.publish(self.topic_publish, json_payload)
            
            # Untuk paho-mqtt 2.1.0, result adalah tuple (reason_code, mid)
            if result.rc == mqtt.MQTTErrorCode.SUCCESS:
                # Print success message
                print(f"{get_current_timestamp_gmt7()} | Action: Publish | Topic: {self.topic_publish} | Data: {payload} | State: Success")
                
                # Log to CSV
                self.log_to_csv(
                    get_current_timestamp_gmt7(),
                    sensor1, sensor2, sensor3, sensor4, sensor5,
                    "Success"
                )
                return True
            else:
                # Print failed message
                print(f"{get_current_timestamp_gmt7()} | Action: Publish | Topic: {self.topic_publish} | State: Failed")
                
                # Log to CSV
                self.log_to_csv(
                    get_current_timestamp_gmt7(),
                    sensor1, sensor2, sensor3, sensor4, sensor5,
                    "Failed"
                )
                return False
                
        except Exception as e:
            error_msg = f"{get_current_timestamp_gmt7()} | Action: Publish | State: Failed - {e}"
            print(error_msg)
            return False