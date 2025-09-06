from function.modbus_handler import ModbusMasterClient
from function.scheduler import SimpleScheduler
from function.help import get_current_timestamp_gmt7

class ModbusMasterApp:
    def __init__(self):
        self.master_client = ModbusMasterClient(host='localhost', port=5020)
        self.scheduler = SimpleScheduler()
        self.status_toggle = 0
    
    def read_sensor_data(self):
        if self.master_client.connect():
            try:
                data = self.master_client.get_all_data()
                
                temperature = data['temperature']
                humidity = data['humidity']
                status = "RUNNING" if data['status'] == 1 else "STOPPED"
                
                print(f"{get_current_timestamp_gmt7()} | Suhu: {temperature}°C | Hum: {humidity}% | Status: {status}")
                
            except Exception as e:
                print(f"{get_current_timestamp_gmt7()} - Error reading sensor data: {e}")
            finally:
                self.master_client.disconnect()
        else:
            print(f"{get_current_timestamp_gmt7()} - Failed to connect to Modbus server")
    
    def toggle_device_status(self):
        if self.master_client.connect():
            try:
                new_status = 1 if self.status_toggle == 0 else 0
                self.status_toggle = new_status
                
                success = self.master_client.write_device_status(new_status)
                status_text = "RUNNING" if new_status == 1 else "STOPPED"
                
                if success:
                    print(f"{get_current_timestamp_gmt7()} - Device status toggled to: {status_text}")
                else:
                    print(f"{get_current_timestamp_gmt7()} - Failed to toggle device status")
                    
            except Exception as e:
                print(f"{get_current_timestamp_gmt7()} - Error toggling device status: {e}")
            finally:
                self.master_client.disconnect()
        else:
            print(f"{get_current_timestamp_gmt7()} - Failed to connect to Modbus server for control")
    
    def run(self):
        print("Modbus TCP Master Client")
        print("Starting client with scheduled tasks...")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        self.scheduler.add_task(5, self.read_sensor_data)
        self.scheduler.add_task(30, self.toggle_device_status)

        print(f"{get_current_timestamp_gmt7()} - Running initial sensor read...")
        self.read_sensor_data()

        try:
            self.scheduler.run()
        except KeyboardInterrupt:
            print(f"\n{get_current_timestamp_gmt7()} - Client stopped by user")
        finally:
            self.scheduler.stop()
            self.master_client.disconnect()

def main():
    master_app = ModbusMasterApp()
    master_app.run()

if __name__ == "__main__":
    main()