from KeyListener import KeyListener
from WindowsScreenMonitor import ActivityMonitor
from MouseListener import MouseListener
from DatabaseManager import DatabaseManager
import threading

def run_window_screen_monitor(activity_monitor):
    activity_monitor.main()

def run_key_listener(key_listener):
    key_listener.main()
    
def run_mouse_listener(mouse_listener):
    mouse_listener.start()

if __name__=="__main__":
    
    database_manager = DatabaseManager()
    timeout = 10
    key_listener = KeyListener(timeout,database_manager)
    
    mouse_listener = MouseListener(timeout=10)

    activity_monitor = ActivityMonitor(database_manager, key_listener, mouse_listener)
   
    screen_monitor_thread = threading.Thread(target = run_window_screen_monitor, args = (activity_monitor,))
    # key_listener_thread = threading.Thread(target = run_key_listener, args = (key_listener,))
    # mouse_listener_thread = threading.Thread(target = run_mouse_listener, args = (mouse_listener,))
    
    screen_monitor_thread.daemon = True    
    # key_listener_thread.daemon = True    
    # mouse_listener_thread.daemon = True    
    
    screen_monitor_thread.start()  
    # key_listener_thread.start()    
    # mouse_listener_thread.start()
    
    
    screen_monitor_thread.join()    
    # key_listener_thread.join()    
    # mouse_listener_thread.join()
    