#!/usr/bin/env python3
"""
Test script for Clock and Uptime widgets
"""

import customtkinter as ctk
from widgets.system_widgets import ClockWidget, UptimeWidget

class TestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("New Widgets Test")
        self.geometry("800x450")
        
        # Test buttons
        test_frame = ctk.CTkFrame(self)
        test_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        clock_btn = ctk.CTkButton(
            test_frame, 
            text="Open Clock Widget", 
            command=self.open_clock,
            width=200,
            height=40
        )
        clock_btn.pack(pady=10)
        
        uptime_btn = ctk.CTkButton(
            test_frame, 
            text="Open Uptime Widget", 
            command=self.open_uptime,
            width=200,
            height=40
        )
        uptime_btn.pack(pady=10)
        
        self.clock_widget = None
        self.uptime_widget = None
    
    def open_clock(self):
        if self.clock_widget is None or not self.clock_widget.winfo_exists():
            self.clock_widget = ClockWidget(self, x=100, y=100)
        else:
            self.clock_widget.show_widget()
    
    def open_uptime(self):
        if self.uptime_widget is None or not self.uptime_widget.winfo_exists():
            self.uptime_widget = UptimeWidget(self, x=500, y=100)
        else:
            self.uptime_widget.show_widget()

if __name__ == "__main__":
    app = TestApp()
    app.mainloop()
