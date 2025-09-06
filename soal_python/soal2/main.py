from function.weather_api import WeatherAPI
from function.scheduler import SimpleScheduler
from function.help import validate_interval_input, get_current_timestamp_gmt7

class WeatherScheduler:
    def __init__(self):
        self.weather_api = WeatherAPI(api_key="d4c99fc363a241e0d1d2bf886e4d231b")
        self.scheduler = SimpleScheduler()
        self.city_name = "Bandung"
    
    def sampling_task(self):
        result = self.weather_api.get_weather_data(self.city_name)
        
        if result['success']:
            save_result = self.weather_api.save_to_json(result['data'])
            
            if save_result:
                temp = result['data']['temperature']
                humidity = result['data']['humidity']
                print(f"{get_current_timestamp_gmt7()} - Success Running Sampling Data Weather with Result Temperature {temp} °C & Humidity {humidity} %")
            else:
                print(f"{get_current_timestamp_gmt7()} - Failed to save data to JSON")
        else:
            status_code = result['status_code']
            message = result['message']
            print(f"{get_current_timestamp_gmt7()} - Failed Running Sampling Data Weather with Status Code {status_code} - {message}")
    
    def get_user_input(self):
        while True:
            try:
                input_str = input("Enter sampling interval in seconds (must be > 0): ")
                is_valid, result = validate_interval_input(input_str)
                
                if is_valid:
                    return result
                else:
                    print(f"Error: {result}")
                    print("Please enter a valid number greater than 0")
            except KeyboardInterrupt:
                print("\nProgram interrupted by user")
                exit()
            except Exception as e:
                print(f"Unexpected error: {e}")
    
    def run(self):
        print("Weather Data Scheduler")
        print("This program will sample weather data from OpenWeather API")
        print(self.city_name)
        print()

        interval_seconds = self.get_user_input()
        
        print(f"\nStarting scheduler with {interval_seconds} seconds interval")
        print("Press Ctrl+C to stop the scheduler")
        print("-" * 50)

        self.scheduler.add_task(interval_seconds, self.sampling_task)

        print(f"{get_current_timestamp_gmt7()} - Running initial sampling...")
        self.sampling_task()

        try:
            self.scheduler.run()
        except KeyboardInterrupt:
            self.scheduler.stop()

def main():
    scheduler = WeatherScheduler()
    scheduler.run()

if __name__ == "__main__":
    main()