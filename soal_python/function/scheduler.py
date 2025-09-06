import time
from datetime import datetime, timedelta
from .help import get_current_timestamp_gmt7

class SimpleScheduler:
    def __init__(self):
        self.tasks = []
        self.running = False
    
    def add_task(self, interval_seconds, task_function, *args, **kwargs):
        task = {
            'interval': interval_seconds,
            'function': task_function,
            'args': args,
            'kwargs': kwargs,
            'last_run': None,
            'next_run': datetime.now()
        }
        self.tasks.append(task)
    
    def run(self):
        self.running = True
        print(f"{get_current_timestamp_gmt7()} - Scheduler started")
        
        try:
            while self.running:
                current_time = datetime.now()
                
                for task in self.tasks:
                    if task['next_run'] <= current_time:
                        try:
                            task['function'](*task['args'], **task['kwargs'])
                        except Exception as e:
                            print(f"{get_current_timestamp_gmt7()} - Error executing task: {e}")

                        task['last_run'] = current_time
                        task['next_run'] = current_time + timedelta(seconds=task['interval'])

                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print(f"\n{get_current_timestamp_gmt7()} - Scheduler stopped by user")
        except Exception as e:
            print(f"{get_current_timestamp_gmt7()} - Scheduler error: {e}")
        finally:
            self.running = False
    
    def stop(self):
        self.running = False
        print(f"{get_current_timestamp_gmt7()} - Scheduler stopped")