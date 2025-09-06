from function.modbus_handler import ModbusSlaveServer
from function.scheduler import SimpleScheduler
from function.help import get_current_timestamp_gmt7
import threading

class ModbusSlaveApp:
    def __init__(self):
        self.slave_server = ModbusSlaveServer(host='localhost', port=5020)
        self.scheduler = SimpleScheduler()
        self.current_status = 0
    
    def update_weather_task(self):
        success = self.slave_server.update_weather_data()
        if success:
            print(f"{get_current_timestamp_gmt7()} - Weather data updated successfully")
        else:
            print(f"{get_current_timestamp_gmt7()} - Failed to update weather data")
    
    def check_status_changes(self):
        if hasattr(self.slave_server, 'context') and self.slave_server.context:
            try:
                slave_context = self.slave_server.context[0]
                current_status = slave_context.getValues(3, 4, count=1)[0]
                
                if current_status != self.current_status:
                    self.current_status = current_status
                    status_text = "RUNNING" if current_status == 1 else "STOPPED"
                    print(f"{get_current_timestamp_gmt7()} - Device status changed to: {status_text}")
            except:
                pass
    
    def run(self):
        print("Modbus TCP Slave Server")
        print("Starting server with scheduled tasks...")
        print("Press Ctrl+C to stop")
        self.scheduler.add_task(5, self.update_weather_task)
        self.scheduler.add_task(1, self.check_status_changes)

        print(f"{get_current_timestamp_gmt7()} - Running initial weather data update...")
        self.update_weather_task()

        scheduler_thread = threading.Thread(target=self.scheduler.run, daemon=True)
        scheduler_thread.start()

        try:
            self.slave_server.run_server()
        except KeyboardInterrupt:
            print(f"\n{get_current_timestamp_gmt7()} - Server stopped by user")
        finally:
            print(f"{get_current_timestamp_gmt7()} - Server stopped")

def main():
    slave_app = ModbusSlaveApp()
    slave_app.run()

if __name__ == "__main__":
    main()