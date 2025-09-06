from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
import json
import os
from datetime import datetime
import struct
import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

class ModbusSlaveServer:
    def __init__(self, host='localhost', port=5020):
        self.host = host
        self.port = port
        self.store = None
        self.context = None
        self.initialize_datastore()
    
    def initialize_datastore(self):
        hr_data = [0] * 10
        
        hr_data[0] = 0  # Temperature part 1
        hr_data[1] = 0  # Temperature part 2  
        hr_data[2] = 0  # Humidity part 1
        hr_data[3] = 0  # Humidity part 2
        hr_data[4] = 0  # Status device (0 atau 1)
        
        store = ModbusSlaveContext(
            hr=ModbusSequentialDataBlock(0, hr_data)
        )
        
        self.context = ModbusServerContext(slaves=store, single=True)
    
    def update_weather_data(self):
        try:
            json_file = "log/data_weather.json"
            if os.path.exists(json_file):
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                if data and len(data) > 0:
                    latest_data = data[-1]
                    
                    temperature = latest_data.get('temperature', 0.0)
                    humidity = latest_data.get('humidity', 0.0)
                    
                    if self.context:
                        slave_context = self.context[0]

                        temp_registers = self.float_to_registers(temperature)
                        humid_registers = self.float_to_registers(humidity)

                        slave_context.setValues(3, 0, [temp_registers[0]])  
                        slave_context.setValues(3, 1, [temp_registers[1]])  
                        slave_context.setValues(3, 2, [humid_registers[0]])  
                        slave_context.setValues(3, 3, [humid_registers[1]])  
                        
                        print(f"Weather data updated: Temp={temperature}°C, Hum={humidity}%")
                        return True
            
            return False
        except Exception as e:
            print(f"Error updating weather data: {e}")
            return False
    
    def float_to_registers(self, value):
        packed = struct.pack('>f', float(value))
        registers = struct.unpack('>HH', packed)
        return registers
    
    def registers_to_float(self, registers):
        if len(registers) >= 2:
            packed = struct.pack('>HH', registers[0], registers[1])
            value = struct.unpack('>f', packed)[0]
            return round(value, 2)
        return 0.0
    
    def get_device_status(self):
        if self.context:
            slave_context = self.context[0]
            status = slave_context.getValues(3, 4, count=1)
            return "RUNNING" if status[0] == 1 else "STOPPED"
        return "UNKNOWN"
    
    def set_device_status(self, status):
        if self.context:
            slave_context = self.context[0]
            slave_context.setValues(3, 4, [status])
            print(f"Device status changed to: {'RUNNING' if status == 1 else 'STOPPED'}")
            return True
        return False
    
    def run_server(self):
        try:
            print(f"Starting Modbus TCP Server on {self.host}:{self.port}")
            print("Holding Registers:")
            print("0-1: Temperature (float, read-only)")
            print("2-3: Humidity (float, read-only)")
            print("4: Device Status (int, read-write)")

            identity = ModbusDeviceIdentification()
            identity.VendorName = 'Python Modbus Server'
            identity.ProductCode = 'PM'
            identity.VendorUrl = 'http://github.com/python-modbus'
            identity.ProductName = 'Modbus Server'
            identity.ModelName = 'Python Modbus'
            identity.MajorMinorRevision = '1.0'
            
            StartTcpServer(
                context=self.context,
                identity=identity,
                address=(self.host, self.port)
            )
            
        except Exception as e:
            print(f"Error starting Modbus server: {e}")

class ModbusMasterClient:
    def __init__(self, host='localhost', port=5020, slave_id=1):
        from pymodbus.client.sync import ModbusTcpClient
        
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.client = ModbusTcpClient(host=host, port=port)
    
    def connect(self):
        return self.client.connect()
    
    def disconnect(self):
        self.client.close()
    
    def read_holding_registers(self, address, count=1):
        try:
            result = self.client.read_holding_registers(address, count, unit=self.slave_id)
            if not result.isError():
                return result.registers
            else:
                print(f"Error reading registers: {result}")
                return None
        except Exception as e:
            print(f"Exception reading registers: {e}")
            return None
    
    def write_register(self, address, value):
        try:
            result = self.client.write_register(address, value, unit=self.slave_id)
            return not result.isError()
        except Exception as e:
            print(f"Exception writing register: {e}")
            return False
    
    def read_temperature(self):
        registers = self.read_holding_registers(0, 2)
        if registers and len(registers) >= 2:
            return self.registers_to_float(registers)
        return 0.0
    
    def read_humidity(self):
        registers = self.read_holding_registers(2, 2)
        if registers and len(registers) >= 2:
            return self.registers_to_float(registers)
        return 0.0
    
    def read_device_status(self):
        registers = self.read_holding_registers(4, 1)
        if registers:
            return registers[0]
        return 0
    
    def write_device_status(self, status):
        return self.write_register(4, status)
    
    def registers_to_float(self, registers):
        if len(registers) >= 2:
            packed = struct.pack('>HH', registers[0], registers[1])
            value = struct.unpack('>f', packed)[0]
            return round(value, 2)
        return 0.0
    
    def get_all_data(self):
        temperature = self.read_temperature()
        humidity = self.read_humidity()
        status = self.read_device_status()
        
        return {
            'temperature': temperature,
            'humidity': humidity,
            'status': status
        }