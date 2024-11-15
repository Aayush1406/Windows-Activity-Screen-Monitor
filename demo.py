import win32gui
import win32con
import win32api
from ctypes import wintypes, windll, Structure, WINFUNCTYPE, POINTER, byref
import ctypes
import datetime

class WindowMonitor:
    def __init__(self):
        self.current_window = None
        self.running = False
        self.window_start_times = {}
        self.window_end_times = {}

    def start_monitoring(self):
        """Start monitoring foreground window changes"""
        self.running = True

        # creates a c-compatible function pointer.
        @WINFUNCTYPE(None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD)
        # Define the callback function
        def win_event_callback(hWinEventHook, event, hwnd, idObject, idChild,dwEventThread, dwmsEventTime):
            if event == win32con.EVENT_SYSTEM_FOREGROUND:
                new_window_title = win32gui.GetWindowText(hwnd)
                if new_window_title != self.current_window:
                    if self.current_window:
                        self.window_end_times[self.current_window] = datetime.datetime.now()
                        print(f"Window '{self.current_window}' was active from {self.window_start_times[self.current_window]} to {self.window_end_times[self.current_window]}")
                    self.current_window = new_window_title
                    self.window_start_times[new_window_title] = datetime.datetime.now()
                    self.on_window_change(new_window_title)

        # Set up event hook
        self.win_event_hook = windll.user32.SetWinEventHook(
            win32con.EVENT_SYSTEM_FOREGROUND,
            win32con.EVENT_SYSTEM_FOREGROUND,
            0,
            win_event_callback,
            0,
            0,
            win32con.WINEVENT_OUTOFCONTEXT | win32con.WINEVENT_SKIPOWNPROCESS
        )

        # Message loop
        msg = wintypes.MSG()
        while self.running and windll.user32.GetMessageW(byref(msg), 0, 0, 0) != 0:
            windll.user32.TranslateMessage(byref(msg))
            windll.user32.DispatchMessageW(byref(msg))

    def stop_monitoring(self):
        """Stop monitoring window changes"""
        self.running = False
        if hasattr(self, 'win_event_hook'):
            windll.user32.UnhookWinEvent(self.win_event_hook)
        if self.current_window:
            self.window_end_times[self.current_window] = datetime.datetime.now()
            print(f"Window '{self.current_window}' was active from {self.window_start_times[self.current_window]} to {self.window_end_times[self.current_window]}")

    def on_window_change(self, new_window_title):
        """Override this method to handle window changes"""
        print(f"Active window changed to: {new_window_title}")

# Example usage
if __name__ == "__main__":
    # Create a custom monitor by inheriting from WindowMonitor
    class MyWindowMonitor(WindowMonitor):
        def on_window_change(self, new_window_title):
            print(f"Window changed! New window: {new_window_title}")
            # Add your custom handling logic here

    # Create and start the monitor
    monitor = MyWindowMonitor()
    try:
        print("Starting window monitor... Press Ctrl+C to stop")
        monitor.start_monitoring()
    except KeyboardInterrupt:
        monitor.stop_monitoring()
        print("\nMonitoring stopped")