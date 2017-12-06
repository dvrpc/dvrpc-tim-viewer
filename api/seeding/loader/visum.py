import pythoncom
import sys
import threading
import win32com.client

class VisumManager(threading.Thread):
    def __init__(self, vernum):
        super(VisumManager, self).__init__()
    def run(self):
        pass

class Visum(threading.Thread):
    def __init__(self):
        super(VisumManager, self).__init__()
    
    def run(self):
        sys.coinit_flags = 0
        pythoncom.CoInitialize()
