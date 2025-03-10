import threading
from pynput import keyboard
import time
from datetime import datetime
from datetime import timedelta

class KeyListener:
    
    def __init__(self):
               
        self.listener = None
        self.restart_listener = None
        self.last_key_time = None
        self.idt_start = 0
        self.idt_stop = 0
        self.idt_duration = 0
        self.active = None
        self.event = threading.Event()
        self.current_id = None
        self.main_monitor_th = None
        self.lock = threading.Lock()
        self.idt_start_active = False
        self.idt_end_active = False
        self.idt_duration_active = False
        self.database_manager = None
        self.current_id_inserted = None
        
        self.key_press_counts = {}
        self.key_hold_times = {}

    def start_listener(self):
        # Start the mouse listener
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        with self.lock:
            self.last_key_time = time.time()
        self.active = True 
                
    def on_press(self, key):
        with self.lock:
            self.last_key_time = time.time()
            # Only reset if we're in idle state
            key_str = str(key)

            if key_str not in self.key_press_counts:
                self.key_press_counts[key_str] = 0
            self.key_press_counts[key_str]+=1

            self.key_hold_times[key_str] = time.time()
            
            self.detect_unusual_behavior(key_str)

            if self.idt_start_active and not self.active:
                self.stop_idle_timer()
                self.calculate_idt_duration()
                self.active = True  

    def detect_unusual_behavior(self, key_str):
        if self.key_press_counts[key_str]>10:
            print(f"Alert: Excessive key press detected for key: {key_str}")
            self.key_press_counts[key_str] = 0

    def on_release(self, key):
        with self.lock:
            key_str = str(key)
            
            if key_str in self.key_hold_times:
                hold_duration = time.time() - self.key_hold_times[key_str]
                if hold_duration > 10:
                    print(f"Alert Key {key_str} held for {hold_duration}")
    
    def stop_listener(self):
        
        if self.listener:
            self.listener.stop()
            self.listener = None
    
    def main_monitor(self):
        
        while True:
            with self.lock:
                idle = time.time() - self.last_key_time > 10
            
            if idle and self.active:
                # print(f"Session {self.current_id} detected idle state.") 3/6
                self.start_idle_timer()
                self.active = False
                self.stop_listener()
            
            if not self.active:
                
                self.event.wait()
                self.event.clear()
            
            time.sleep(1)
            
    def start_idle_timer(self):
        if self.idt_start_active == False:
            self.idt_start = time.time()
            self.idt_start_active = True
            # print(f"Idle period started for [{self.current_id}] at", datetime.fromtimestamp(self.idt_start)) 3/6
            
    def stop_idle_timer(self):
        if self.idt_start_active:
            self.idt_stop = time.time()
            # print("Idle period stopped at", datetime.fromtimestamp(self.idt_stop)) 3/6
            self.calculate_idt_duration()

            self.idt_start_active = False
            

    def calculate_idt_duration(self):
        # Calculate the duration and add it to total idle duration
        if self.idt_start and self.idt_stop:
            idle_time = self.idt_stop - self.idt_start
            self.idt_duration += idle_time
            # print("Idle duration for this period:", idle_time, "seconds") 3/6
            # print("Total idle duration for current session:", self.idt_duration, "seconds") 3/6

    def on_press_restart(self, key):
        if not self.active:
            self.stop_idle_timer()
            # self.calculate_idt_duration()
            self.start_listener()
            self.event.set()  # Resume main monitor loop
            print("Listener restarted!")

    def start_listener_monitor(self):

        self.restart_listener = keyboard.Listener(on_press=self.on_press_restart)
        self.restart_listener.start()
            
    def set_process_id_for_keyListener(self, session_id):
        if self.current_id != session_id:
            if self.current_id is not None:
                if self.idt_start_active or self.current_id_inserted==False:
                    self.stop_idle_timer()
                    # self.calculate_idt_duration()
                    
                    # print(f"Key Listener Session[{self.current_id}] total idle duration = {self.idt_duration}") 3/6
                    formatted_duration = str(timedelta(seconds=self.idt_duration))
                    self.database_manager.dump_keyListener_session_to_db(self.current_id, formatted_duration)
                    self.current_id_inserted = True
            
            # Reset for the new session
            # print(f"Starting new session Session[{session_id}]") 3/6
            self.current_id = session_id
            self.current_id_inserted = False
            self.reset()
            
    def reset(self):
        with self.lock:
            self.last_key_time = time.time()
        self.idt_start = 0
        self.idt_stop = 0
        self.idt_duration = 0
        self.idt_duration_active = False
        self.idt_start_active = False
        self.event.set()
    
    def main(self, session_id, database_manager):
        self.database_manager = database_manager
        self.set_process_id_for_keyListener(session_id)
        # print("Session _ id = ", session_id) 3/6
        
        if self.listener is None:
            self.start_listener()
        
        if self.restart_listener is None:
            start_listener_monitor_th = threading.Thread(target=self.start_listener_monitor)
            start_listener_monitor_th.daemon = True
            start_listener_monitor_th.start()
        
        if self.main_monitor_th is None:
            self.main_monitor_th = threading.Thread(target=self.main_monitor)
            self.main_monitor_th.daemon = True        
            self.main_monitor_th.start()



