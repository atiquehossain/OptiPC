#!/usr/bin/env python3
"""
Simple test script to verify the Calendar Widget works correctly
"""

import customtkinter as ctk
from widgets.system_widgets import CalendarWidget

class TestApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Calendar Widget Test")
        self.geometry("400x450")
        
        # Test button
        test_btn = ctk.CTkButton(
            self, 
            text="Open Calendar Widget", 
            command=self.open_calendar
        )
        test_btn.pack(pady=20)
        
        self.calendar_widget = None
    
    def open_calendar(self):
        if self.calendar_widget is None or not self.calendar_widget.winfo_exists():
            self.calendar_widget = CalendarWidget(self, x=100, y=100)
        else:
            self.calendar_widget.show_widget()

if __name__ == "__main__":
    app = TestApp()
    app.mainloop()
