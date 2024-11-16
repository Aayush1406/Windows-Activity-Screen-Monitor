# Save this as process_monitor.py

import psutil
import win32gui
import win32process
import win32api
import win32con
import win32security
import ctypes
from ctypes import wintypes
from datetime import datetime
import os
from typing import Dict, Any

class EnhancedProcessMonitor:
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi

    def __init__(self):
        self.current_handle = self.user32.GetForegroundWindow()
        self.current_pid = self._get_foreground_process_id()

    def _get_foreground_process_id(self):            
        handle = self.user32.GetForegroundWindow() 
        pid = wintypes.DWORD()            
        self.user32.GetWindowThreadProcessId(handle, ctypes.byref(pid))
        return pid.value

    def _get_executable_path(self):
        try:
            process_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, self.current_pid)
            executable_path = win32process.GetModuleFileNameEx(process_handle, 0)
            win32api.CloseHandle(process_handle)
            return executable_path
        except Exception as e:
            return None

    def _get_window_title(self): 
        return win32gui.GetWindowText(self.current_handle)

    def _get_process_create_time(self):
        try:
            process = psutil.Process(self.current_pid)    
            process_create_time = datetime.fromtimestamp(process.create_time())        
            return process_create_time
        except Exception:
            return datetime.now()

    def _get_process_name(self):
        try:
            process = psutil.Process(self.current_pid)
            process_name = process.name()
            return process_name
        except psutil.NoSuchProcess:
            return "No Such Process"
        
    def _get_process_status(self):
        try:
            process = psutil.Process(self.current_pid)
            process_status = process.status()
            return process_status
        except Exception:
            return "UNKNOWN"

    def get_process_metrics(self) -> Dict[str, Any]:
        """Gather comprehensive metrics about the current foreground process"""
        metrics = {
            # Basic Process Info
            'pid': self.current_pid,
            'name': self._get_process_name(),
            'executable_path': self._get_executable_path(),
            'window_title': self._get_window_title(),
            'create_time': self._get_process_create_time(),
            'status': self._get_process_status(),
            
            # Resource Usage
            'cpu_usage': self._get_cpu_usage(),
            'memory_usage': self._get_memory_usage(),
            'io_counters': self._get_io_counters(),
            'network_connections': self._get_network_connections(),
            
            # Window Information
            'window_placement': self._get_window_placement(),
            'window_state': self._get_window_state(),
            
            # Process Details
            'threads_count': self._get_threads_count(),
            'handles_count': self._get_handles_count(),
            
            # User Context
            'username': self._get_process_username(),
            'session_id': self._get_session_id(),
        }
        return metrics

    def _get_cpu_usage(self) -> float:
        try:
            process = psutil.Process(self.current_pid)
            return process.cpu_percent(interval=0.1)
        except Exception:
            return 0.0

    def _get_memory_usage(self) -> Dict[str, int]:
        try:
            process = psutil.Process(self.current_pid)
            mem_info = process.memory_info()
            return {
                'rss': mem_info.rss,  # Resident Set Size
                'vms': mem_info.vms,  # Virtual Memory Size
                'private': getattr(mem_info, 'private', 0),  # Private Memory
                'shared': getattr(mem_info, 'shared', 0)  # Shared Memory
            }
        except Exception:
            return {}

    def _get_io_counters(self) -> Dict[str, int]:
        try:
            process = psutil.Process(self.current_pid)
            io = process.io_counters()
            return {
                'read_bytes': io.read_bytes,
                'write_bytes': io.write_bytes,
                'read_count': io.read_count,
                'write_count': io.write_count
            }
        except Exception:
            return {}

    def _get_network_connections(self) -> list:
        try:
            process = psutil.Process(self.current_pid)
            connections = process.connections()
            return [{
                'local_addr': {'ip': c.laddr.ip, 'port': c.laddr.port} if c.laddr else None,
                'remote_addr': {'ip': c.raddr.ip, 'port': c.raddr.port} if c.raddr else None,
                'status': c.status,
                'type': c.type
            } for c in connections]
        except Exception:
            return []

    def _get_threads_count(self) -> int:
        try:
            process = psutil.Process(self.current_pid)
            return len(process.threads())
        except Exception:
            return 0

    def _get_handles_count(self) -> int:
        try:
            process = psutil.Process(self.current_pid)
            return process.num_handles()
        except Exception:
            return 0

    def _get_window_placement(self) -> Dict[str, Any]:
        try:
            rect = win32gui.GetWindowRect(self.current_handle)
            return {
                'left': rect[0],
                'top': rect[1],
                'right': rect[2],
                'bottom': rect[3],
                'width': rect[2] - rect[0],
                'height': rect[3] - rect[1]
            }
        except Exception:
            return {}

    def _get_window_state(self) -> str:
        try:
            placement = win32gui.GetWindowPlacement(self.current_handle)
            states = {
                1: "NORMAL",
                2: "MINIMIZED",
                3: "MAXIMIZED"
            }
            return states.get(placement[1], "UNKNOWN")
        except Exception:
            return "UNKNOWN"

    def _get_process_username(self) -> str:
        try:
            process = psutil.Process(self.current_pid)
            return process.username()
        except Exception:
            return ""

    def _get_session_id(self) -> int:
        try:
            process = psutil.Process(self.current_pid)
            return process.sessionid()
        except Exception:
            return -1