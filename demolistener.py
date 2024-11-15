import threading
from pynput import keyboard
import time

def main_monitor():
    pass
    # print(f"pressed {key}")
    
if __name__ == "__main__":
    
    th = threading.Thread(target = main_monitor)
    print("1 = ",th)
    # th.daemon = True
    th.start()
    
    print("2 = ",th.is_alive())
    
    while True:
        time.sleep(1)