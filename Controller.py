from KeyListener import KeyListener
from ProcessMonitor import ProcessMonitor
from MouseListener import MouseListener
from DatabaseManager import DatabaseManager
from WindowMonitor import WindowMonitor
import threading

class Controller:
    def __init__(self):
        self.window_monitor = WindowMonitor()
        
        self.process_monitor = ProcessMonitor(self.window_monitor)

        self.database_manager = DatabaseManager()

    
    def run_window_monitor(self):
        self.window_monitor.main(self.process_monitor,self.database_manager)

if __name__=="__main__":          

    controller = Controller()
    window_monitor_thread = threading.Thread(target = controller.run_window_monitor)
    
    window_monitor_thread.daemon = True

    window_monitor_thread.start()    
    
    window_monitor_thread.join()
    
   
    