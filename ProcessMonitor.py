import psutil 
import ctypes  
import ctypes.wintypes
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
from WindowMonitor import WindowMonitor

class ProcessMonitor:
    
    TIME_INTERVAL = 1
    user32 = ctypes.windll.user32     
    
    def __init__(self, window_monitor):
        

        self.current_pid = None
        self.current_handle = None
        self.executable_path = None
        self.child_name = None
        self.window_title = None
        self.process_create_time = None
        self.process_name = None
        self.process_status = None    
          
    #Utlility Methods:            

    def print_foreground_process_details(self,handle):
        self.current_handle = handle   
        self.set_foreground_process_details()     
        print("Window Title = ",self.window_title)      
        print("Process Name = ",self.process_name)    
        print("Process id = ",self.current_pid)
        print("Process Status = ",self.process_status)    
        print("Child Name = ",self.child_name)    
        print("Executable Path = ",self.executable_path)        
        print("Process Create Time = ",self.process_create_time)    
        print("Handle = ",self.current_handle)       
        
    def set_foreground_process_details(self):
        self.current_pid = self._get_foreground_process_id()
        self.executable_path = self._get_executable_path()
        self.child_name = self._get_uwp_app_name()
        self.window_title = self._get_window_title()
        self.process_create_time = self._get_process_create_time()                
        self.process_name = self._get_process_name()
        self.process_status = self._get_process_status()
    
    def get_foreground_process_details_dict(self,handle): 
        self.current_handle = handle 
        self.set_foreground_process_details()
        foreground_process_details_dict = {
            "executable_path": self.executable_path,
            "child_name": self.child_name,
            "window_title": self.window_title,
            "process_create_time": self.process_create_time,
            "process_name": self.process_name,
            "process_status": self.process_status,
            "current_pid": self.current_pid,
            "current_handle": self.current_handle
         }         
        return foreground_process_details_dict
    
    #Process Retrieval Methods:
    
    def _get_foreground_process_id(self):            
        handle = ProcessMonitor.user32.GetForegroundWindow() 
        pid = wintypes.DWORD()            
        ProcessMonitor.user32.GetWindowThreadProcessId(handle, ctypes.byref(pid))
        return pid.value

    def _get_executable_path(self):
        try:
            process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, self.current_pid)
            executable_path = win32process.GetModuleFileNameEx(process_handle, 0)
            win32api.CloseHandle(process_handle)
            return executable_path
        except Exception as e:
            return None
        
    def _get_uwp_app_name(self):
        try:
            process = psutil.Process(self.current_pid)
            for child in process.children(recursive=True):
                return child.name()
        except Exception as e:
            return None
        

    def _get_window_title(self): 
        return win32gui.GetWindowText(self.current_handle)

    def _get_process_create_time(self):
        process = psutil.Process(self.current_pid)    
        process_create_time = datetime.fromtimestamp(process.create_time())        
        return process_create_time

    def _get_process_name(self):
        try:
            process = psutil.Process(self.current_pid)
            process_name = process.name()
            return process_name
        except psutil.NoSuchProcess:
            return "No Such Process"
        
    def _get_process_status(self):
        process = psutil.Process(self.current_pid)
        process_status = process.status()
        return process_status
 
    
    #Database Interaction Methods:
    
    # def insert_foreground_process_details(self):        
    #     foreground_process_details_dict = self.get_foreground_process_details_dict()
    #     self.database_manager.insert_foreground_process_details_in_db(foreground_process_details_dict)
            
    # def set_window_end_time(self):
    #     self.database_manager.insert_window_end_time_in_db(self.old_pid)               
        
    # def set_window_start_time(self):
    #     self.set_window_status_to_active()    
    #     self.database_manager.insert_window_start_time_in_db(self.current_pid)        

    # def set_window_status_to_active(self):
    #     self.database_manager.insert_window_status_to_active_in_db(self.current_pid)

    # def set_window_status_to_inactive(self):      
    #     self.database_manager.insert_window_status_to_inactive_in_db(self.old_pid)

    # def set_process_status(self):
    #    print("Set Process Status OLD PID = ", self.old_pid)
    #    process_name = self._get_process_name(self.old_pid)
    #    print("Set Process Status process name = ", process_name)       
    #    self.database_manager.insert_process_status_in_db(self.old_pid,process_name)
       
    # def set_process_duration(self):
    #     self.database_manager.set_process_duration_in_db(self.old_pid)
    #     self.set_window_status_to_inactive()




