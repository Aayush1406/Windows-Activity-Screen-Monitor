from ctypes import windll, wintypes, byref, WINFUNCTYPE
import win32con
import win32gui
import datetime
from KeyListener import KeyListener
from MouseListener import MouseListener

class WindowMonitor:
    
    # Constructor
    def __init__(self):   
        self.running = False
        self.current_window = None
        self.win_start_time = {}
        self.duration = None
        self.win_event_hook = None
        self.ignore_ls = ["","Task Switching"]
        self.current_handle = None
        self.process_monitor = None
        self.current_session_id = None
        self.database_manager = None
        self.key_listener = KeyListener()
        self.mouse_listener = MouseListener()
        
        
    def start_monitoring(self):
        
        self.running = True
        
        #Callback.
        @WINFUNCTYPE(None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD)
        def win_event_callback(hWinEventHook, event, hwnd, idObject, idChild, dwEventThread, dwmsEventTime):
            if event == win32con.EVENT_SYSTEM_FOREGROUND:
                self.handle_window_change(hwnd)
                
        #Register the event hook.
        self.win_event_hook = windll.user32.SetWinEventHook(
            win32con.EVENT_SYSTEM_FOREGROUND,  
            win32con.EVENT_SYSTEM_FOREGROUND,  
            0,                                 
            win_event_callback,                
            0,                                
            0,                                
            win32con.WINEVENT_OUTOFCONTEXT | win32con.WINEVENT_SKIPOWNPROCESS
        )
        self.run_message_loop()
        
    def run_message_loop(self):
        # Create msg struct
        # MSG structure contains:
        # hwnd:    Window handle
        # message: Message ID/type
        # wParam:  Additional data (depends on message type)
        # lParam:  Additional data (depends on message type)
        # time:    Time message was posted
        # pt:      Mouse position when message was posted    
        msg = wintypes.MSG()
    
        while self.running:
            #byref(msg) is pointer to msg struct.
            #GetMessageW is a blocking function. It suspends the thread's execution until msg is avail.
            message_result = windll.user32.GetMessageW(byref(msg), 0, 0, 0)
            
            if message_result > 0:
                windll.user32.TranslateMessage(byref(msg))                
                windll.user32.DispatchMessageW(byref(msg))
            
    
    def handle_window_change(self,hwnd):
        
        new_window_title = win32gui.GetWindowText(hwnd)
        
        if new_window_title not in self.ignore_ls:    
            if new_window_title != self.current_window:
                
                if self.current_window and self.current_session_id is not None:
                    end_time = datetime.datetime.now()
                    start_time = self.win_start_time[self.current_window]
                    duration = end_time - start_time
                    # self.update_window_end(self.current_session_id,end_time,duration)
                    print(f"Duration = {duration}")                                   
                    print("window end time = ",end_time)
                    self.update_window_end(self.current_session_id, end_time, duration)
                                    
                self.current_window = new_window_title
                self.win_start_time[new_window_title] = datetime.datetime.now()
                self.current_handle = hwnd        
                self.on_window_change(new_window_title, hwnd)

            
    def on_window_change(self, new_window_title, hwnd):
        print("------------------------------------")

        foreground_details_dict = self.process_monitor.get_foreground_process_details_dict(hwnd)
        # self.process_monitor.print_foreground_process_details(self.current_handle)
        # print("window start time = ",self.win_start_time.get(self.current_window))
        foreground_details_dict['window_start_time'] = self.win_start_time.get(self.current_window) 
        self.current_session_id = self.insert_window_start(foreground_details_dict)
        self.mouse_listener.main(self.current_session_id,self.database_manager)
        self.key_listener.main(self.current_session_id,self.database_manager)        

    def insert_window_start(self,foreground_details_dict):
        print(foreground_details_dict)
        return self.database_manager.insert_window_start_db(foreground_details_dict)        
    
    def update_window_end(self,current_session_id, end_time, duration):
        self.database_manager.update_window_end_db(current_session_id, end_time, duration)
       
    def main(self, process_monitor,database_manager):
       
        try:
            self.process_monitor = process_monitor
            self.database_manager = database_manager
            print("Starting window monitor... Press Ctrl+C to stop")
            self.start_monitoring()
        except KeyboardInterrupt:
            self.stop_monitoring()
            print("\nMonitoring stopped")            