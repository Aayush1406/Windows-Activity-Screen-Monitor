import threading
import time
from pynput import keyboard
from DatabaseManager import DatabaseManager

class KeyListener:
    
    def __init__(self, timeout, database_manager):
        self.timeout = timeout  
        self.last_key_time = time.time()  
        self.listener = None  
        self.timer_thread = None  
        self.active = False  
        self.restart_event = threading.Event()
        self.idle_start_time = 0
        self.idle_end_time = 0
        self.idle_duration = 0 
        self.current_pid = None
        self.old_pid = None
        self.database_manager = database_manager

    def on_press(self, key):
        self.last_key_time = time.time()
        print(f"pressed {key}")

    def start_listener(self):
        if  self.active==False:
            self.listener = keyboard.Listener(on_press=self.on_press)
            self.listener.start()
            self.active = True
            self.last_key_time = time.time()
            print("Listener started")

    def stop_listener(self):
        if self.listener is not None:
            print("No key pressed for a minute, stopping listener...")
            self.listener.stop()
            self.listener = None
            self.active = False

    def monitor_activity(self):
        while True:
            # Check for inactivity
            if self.active == True and (time.time() - self.last_key_time) > self.timeout: # active == True is needed as if the start_listener is never started than 
                
                self.stop_listener()

            # Wait for the restart event to be set, which happens on any key press
            if self.active == False:
                print("Waiting for key press to restart listener...")
                self.start_idle_time()
                self.restart_event.wait()  # Block until the event is set
                self.restart_event.clear()  # Clear the event after restarting the list
                print("here!!!")
                self.start_listener()

            time.sleep(1)  # Avoid busy waiting, check every second
    
    def start_idle_time(self):
        print("Idle time calculation started......")
        self.idle_start_time = time.time()
        
    def end_idle_time(self):
        print("Idle time calculation end......")
        self.idle_end_time = time.time()
    
    def calculate_idle_duration(self):
        self.idle_duration = self.idle_duration + self.idle_end_time - self.idle_start_time 
        
        print("Idle duration = ", self.idle_duration)        


    def monitor_keypress_for_restart(self):
        # This method will always run a lightweight listener to catch key presses
        def on_press_restart(key):
            if self.active == False:
                self.restart_event.set()  # Set the event to restart the main listener
                self.end_idle_time()
                self.calculate_idle_duration()

        # This listener will always be active, independent of the main listener
        restart_listener = keyboard.Listener(on_press=on_press_restart)
        restart_listener.start()
        
    def set_process_id_for_keyListener(self,current_pid):
        

        if self.current_pid != current_pid:
            if self.current_pid is not None:
                self.end_idle_time()
                self.calculate_idle_duration()  # Calculate the idle duration for the old PID
                print(f"Idle Duration for PID {self.old_pid}: {self.idle_duration} seconds")  # Print idle duration for the old process
                
            # Reset and switch to the new PID
            self.old_pid = self.current_pid  # Store the old PID
            self.current_pid = current_pid  # Update the current PID
            print(f"Switching to new PID: {self.current_pid}")
            
            # Reset the idle timer for the new PID
            self.reset_key_listener()
            self.main()
            
   

    def reset_key_listener(self):
        self.idle_start_time = 0
        self.idle_end_time = 0
        self.idle_duration = 0 
        self.last_key_time = time.time() 

    def start(self):


        self.start_listener() # call the start_listener() method.
        
        self.timer_thread = threading.Thread(target=self.monitor_activity)        
        self.timer_thread.daemon = True  # Daemon thread will automatically stop when the program exits        
        self.timer_thread.start()

        # Start the restart monitoring thread
        restart_thread = threading.Thread(target=self.monitor_keypress_for_restart)
        restart_thread.daemon = True
        restart_thread.start()

    def main(self):

        self.start()
        