import sys
import os
import time
import signal

from function.mqtt_handler import MQTTClient
from function.scheduler import SimpleScheduler
from function.help import get_current_timestamp_gmt7

class MQTTApp:
    def __init__(self):
        self.mqtt_client = MQTTClient()
        self.scheduler = SimpleScheduler()
        self.running = True
    
    def setup_signal_handlers(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        print(f"\n{get_current_timestamp_gmt7()} - Received shutdown signal")
        self.stop()
    
    def publish_task(self):
        self.mqtt_client.publish_data()
    
    def initialize(self):
        print("=== MQTT Client Application ===")
        print("Broker: test.mosquitto.org")
        print(f"Publish Topic: {self.mqtt_client.topic_publish}")
        print(f"Subscribe Topic: {self.mqtt_client.topic_subscribe}")
        print("Initial interval: 5 seconds")
        print("Press Ctrl+C to stop the application")
        print("-" * 60)

        if not self.mqtt_client.create_csv_logger():
            print(f"{get_current_timestamp_gmt7()} - Warning: CSV logging might not work")

        print(f"{get_current_timestamp_gmt7()} - Connecting to MQTT broker...")
        if not self.mqtt_client.connect():
            print(f"{get_current_timestamp_gmt7()} - Failed to connect to MQTT broker")
            return False

        time.sleep(2)
        
        if not self.mqtt_client.is_connected:
            print(f"{get_current_timestamp_gmt7()} - Not connected to MQTT broker")
            return False
        
        return True
    
    def run(self):
        if not self.initialize():
            return

        self.setup_signal_handlers()

        self.scheduler.add_task(self.mqtt_client.interval, self.publish_task)

        print(f"{get_current_timestamp_gmt7()} - Running initial publish...")
        self.publish_task()

        try:
            while self.running:
                current_interval = self.mqtt_client.interval
                
                if len(self.scheduler.tasks) > 0 and self.scheduler.tasks[0]['interval'] != current_interval:
                    self.scheduler.tasks[0]['interval'] = current_interval
                    print(f"{get_current_timestamp_gmt7()} - Interval updated to {current_interval} seconds")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print(f"\n{get_current_timestamp_gmt7()} - Application stopped by user")
        except Exception as e:
            print(f"{get_current_timestamp_gmt7()} - Application error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        self.running = False
        self.scheduler.stop()
        self.mqtt_client.disconnect()
        print(f"{get_current_timestamp_gmt7()} - Application stopped")

def main():
    app = MQTTApp()
    app.run()

if __name__ == "__main__":
    main()