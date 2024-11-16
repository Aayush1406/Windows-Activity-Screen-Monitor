import threading
from pynput import keyboard
import time
from datetime import datetime, timedelta

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
        self.database_manager = None
        self.current_id_inserted = None

        # New variables for detecting unusual behavior
        self.key_press_counts = {}
        self.key_hold_times = {}
        self.alert_thresholds = {
            'max_key_presses': 50,  # Max presses in 10 seconds
            'prolonged_key_hold': 5  # Key held for more than 5 seconds
        }
        self.start_working_hours = datetime.strptime("09:00", "%H:%M").time()
        self.end_working_hours = datetime.strptime("17:00", "%H:%M").time()

    def start_listener(self):
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        with self.lock:
            self.last_key_time = time.time()
        self.active = True

    def on_press(self, key):
        with self.lock:
            self.last_key_time = time.time()
            key_str = str(key)

            # Track key press count
            if key_str not in self.key_press_counts:
                self.key_press_counts[key_str] = 0
            self.key_press_counts[key_str] += 1

            # Start tracking key hold time
            self.key_hold_times[key_str] = time.time()

            # Check for unusual activity
            self.detect_unusual_behavior(key_str)

            if self.idt_start_active and not self.active:
                self.stop_idle_timer()
                self.calculate_idt_duration()
                self.active = True

    def on_release(self, key):
        with self.lock:
            key_str = str(key)

            # Calculate hold duration
            if key_str in self.key_hold_times:
                hold_duration = time.time() - self.key_hold_times[key_str]
                if hold_duration > self.alert_thresholds['prolonged_key_hold']:
                    print(f"Alert: Key '{key_str}' held for {hold_duration:.2f} seconds.")

                del self.key_hold_times[key_str]

    def detect_unusual_behavior(self, key_str):
        # Check for excessive key presses
        if self.key_press_counts[key_str] > self.alert_thresholds['max_key_presses']:
            print(f"Alert: Excessive key presses detected for '{key_str}'.")
            self.key_press_counts[key_str] = 0  # Reset count after alert

        # Check for activity outside working hours
        current_time = datetime.now().time()
        if not (self.start_working_hours <= current_time <= self.end_working_hours):
            print(f"Alert: Activity detected outside working hours.")

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
            self.listener = None

    def main_monitor(self):
        while True:
            with self.lock:
                idle = time.time() - self.last_key_time > 10

            if idle and self.active:
                print(f"Session {self.current_id} detected idle state.")
                self.start_idle_timer()
                self.active = False
                self.stop_listener()

            if not self.active:
                self.event.wait()
                self.event.clear()

            time.sleep(1)

    def start_idle_timer(self):
        if not self.idt_start_active:
            self.idt_start = time.time()
            self.idt_start_active = True
            print(f"Idle period started for [{self.current_id}] at", datetime.fromtimestamp(self.idt_start))

    def stop_idle_timer(self):
        if self.idt_start_active:
            self.idt_stop = time.time()
            print("Idle period stopped at", datetime.fromtimestamp(self.idt_stop))
            self.calculate_idt_duration()
            self.idt_start_active = False

    def calculate_idt_duration(self):
        if self.idt_start and self.idt_stop:
            idle_time = self.idt_stop - self.idt_start
            self.idt_duration += idle_time
            print("Idle duration for this period:", idle_time, "seconds")
            print("Total idle duration for current session:", self.idt_duration, "seconds")

    def start_listener_monitor(self):
        self.restart_listener = keyboard.Listener(on_press=self.on_press_restart)
        self.restart_listener.start()

    def on_press_restart(self, key):
        if not self.active:
            self.stop_idle_timer()
            self.start_listener()
            self.event.set()
            print("Listener restarted!")

    def main(self, session_id, database_manager):
        self.database_manager = database_manager
        self.current_id = session_id
        print("Session ID:", session_id)

        if self.listener is None:
            self.start_listener()

        if self.restart_listener is None:
            threading.Thread(target=self.start_listener_monitor, daemon=True).start()

        if self.main_monitor_th is None:
            self.main_monitor_th = threading.Thread(target=self.main_monitor, daemon=True)
            self.main_monitor_th.start()
