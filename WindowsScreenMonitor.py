import psutil 
import ctypes  
from ctypes import wintypes 
import time
import datetime
import win32api
import win32con
import win32process
import win32gui
from datetime import datetime
import pypyodbc as odbc
import pyodbc
from mysql.connector import pooling
from DatabaseManager import DatabaseManager

class Titlebarinfo(ctypes.Structure):
    
    _fields_ = [("cbSize",wintypes.DWORD),
                ("rcTitleBar",wintypes.RECT),
                ("rgstate",wintypes.DWORD*6)]

class ActivityMonitor:
    
    TIME_INTERVAL = 1
    user32 = ctypes.windll.user32     
    
    def __init__(self, database_manager, key_listener, mouse_listener):
        
        self.old_pid = None
        self.old_handle = None
        self.current_pid = None 
        self.current_handle = None
        self.executable_path = None,
        self.child_name = None,
        self.title_bar_info = None,
        self.window_title = None,
        self.process_create_time = None,
        self.process_name = None,
        self.process_status = None,    
        self.database_manager = database_manager
        self.key_listener = key_listener
        self.mouse_listener = mouse_listener

    
    def get_foreground_process_id(self):
            
        handle = ActivityMonitor.user32.GetForegroundWindow() 
        pid = wintypes.DWORD()            
        ActivityMonitor.user32.GetWindowThreadProcessId(handle, ctypes.byref(pid))  
        return pid.value, handle



    def get_title_bar_info(self):
        titleBarInfo = Titlebarinfo()        
        titleBarInfo.cbSize = ctypes.sizeof(Titlebarinfo)
        self.user32.GetTitleBarInfo(self.current_handle,ctypes.byref(titleBarInfo))    
        return titleBarInfo

    def get_executable_path_from_Pid(self):
        try:
            process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, self.current_pid)
            executable_path = win32process.GetModuleFileNameEx(process_handle, 0)
            win32api.CloseHandle(process_handle)
            print("Executable Path =  ",executable_path)
            return executable_path
        except Exception as e:
            return None
        
    def get_uwp_app_name(self):
        try:
            process = psutil.Process(self.current_pid)
            for child in process.children(recursive=True):
                return child.name()
        except Exception as e:
            return None
        
    class TITLEBARINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD),
                    ("rcTitleBar", wintypes.RECT),
                    ("rgstate", wintypes.DWORD * 6)]    


    def get_window_title(self): 

        if self.current_handle != self.old_handle:
            return win32gui.GetWindowText(self.current_handle)

    def calculateTimeForHandle(self,currentTime, currentHandle, pid):
        process = psutil.Process(pid)
        processStartTime = process.create_time()
        processStartTime = datetime.fromtimestamp(processStartTime)
        processStartTime = processStartTime.strftime('%H:%M:%S')
        
        duration = datetime.strptime(currentTime,'%H:%M:%S' ) - datetime.strptime(processStartTime,'%H:%M:%S')
        return duration

    def get_process_create_time(self):
        process = psutil.Process(self.current_pid)    
        process_create_time = datetime.fromtimestamp(process.create_time())        
        print(process_create_time)
        return process_create_time

    def get_process_name(self,pid):
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            return process_name
        except psutil.NoSuchProcess:
            return "No Such Process"
        
    def get_process_status(self):
        process = psutil.Process(self.current_pid)
        process_status = process.status()
        return process_status

    def print_foreground_details(self):
        
        print("-----------------------------------------")    
        print("Window Title = ",self.window_title)      
        print("Process Name = ",self.process_name)    
        print("Process id = ",self.current_pid)
        print("Process Status = ",self.process_status)    
        print("Child Name = ",self.child_name)    
        print("Executable Path = ",self.executable_path)        
        print("Process Create Time = ",self.process_create_time)    
        print("Handle = ",self.current_handle) 
        
        
    def set_foreground_process_details(self):

        self.executable_path = self.get_executable_path_from_Pid()
        self.child_name = self.get_uwp_app_name()
        self.title_bar_info = self.get_title_bar_info()
        self.window_title = self.get_window_title()
        self.process_create_time = self.get_process_create_time()                
        self.process_name = self.get_process_name(self.current_pid)
        self.process_status = self.get_process_status()
    
    def get_foreground_process_details_dict(self):
         
         foreground_process_details_dict = {
            "executable_path": self.executable_path,
            "child_name": self.child_name,
            "title_bar_info": self.title_bar_info,
            "window_title": self.window_title,
            "process_create_time": self.process_create_time,
            "process_name": self.process_name,
            "process_status": self.process_status,
            "current_pid": self.current_pid,
            "current_handle": self.current_handle
         }
         
         return foreground_process_details_dict

    def insert_foreground_process_details(self):
        
        foreground_process_details_dict = self.get_foreground_process_details_dict()
        self.database_manager.insert_foreground_process_details_in_db(foreground_process_details_dict)

            
    def set_window_end_time(self):
        self.database_manager.set_window_end_time_in_db(self.old_pid)
        
                
        
    def set_window_start_time(self):

        self.set_window_status_to_active()    
        self.database_manager.set_window_start_time_in_db(self.current_pid)
        

    def set_window_status_to_active(self):

        self.database_manager.insert_window_status_to_active_in_db(self.current_pid)
        


    def set_window_status_to_inactive(self):
        
        self.database_manager.insert_window_status_to_inactive_in_db(self.old_pid)




    def set_process_status(self):
       process_name = self.get_process_name(self.old_pid)
       self.database_manager.set_process_status_in_db(self.old_pid,process_name)

        
    def set_process_duration(self):
        
        self.database_manager.set_process_duration_in_db(self.old_pid)
        
        self.set_window_status_to_inactive()

            
        
    def keep_running_script(self):

        while True:
            
            self.current_pid, self.current_handle = self.get_foreground_process_id()

            
            if self.old_pid != self.current_pid and self.old_handle != self.current_handle and self.current_pid!= 22824:
                self.key_listener.set_process_id_for_keyListener(self.current_pid)
                self.set_foreground_process_details()
                self.print_foreground_details()
                self.insert_foreground_process_details()                                   
                self.set_window_start_time()
                self.set_window_end_time()
                self.set_process_status()
                self.set_process_duration()
                   
                
            self.old_pid = self.current_pid
            self.old_handle = self.current_handle   
            time.sleep(ActivityMonitor.TIME_INTERVAL)


    def main(self):

        self.keep_running_script()
        
        
    
if __name__ == "__main__":
    
    database_manager = DatabaseManager()
    employee_activity_monitor = ActivityMonitor(database_manager)
    employee_activity_monitor.main()